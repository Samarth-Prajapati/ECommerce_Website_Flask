import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

def initialize_rag():
    """Initialize the RAG pipeline with Hugging Face embeddings and Groq LLM."""
    # Load extracted data
    loader = TextLoader("extracted_data.txt", encoding="utf-8")
    documents = loader.load()

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    # Create embeddings with Hugging Face
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Create and save FAISS vector store
    vectorstore = FAISS.from_documents(texts, embeddings)
    vectorstore.save_local("faiss_index")

def get_chatbot_response(query):
    """Get response from the chatbot using RAG with Groq."""
    # Load vector store
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

    # Initialize Groq LLM
    llm = ChatGroq(model_name="llama3-8b-8192", groq_api_key=GROQ_API_KEY, temperature=0.3)

    # Define prompt template
    prompt_template = """
    You are a friendly and precise assistant for an e-commerce website called Shopify. 
    Answer the user's query based on the provided context. Format the response as a bullet-point list (using `-`) for lists of items (e.g., products, users, categories).
    **Always include navigation links in HTML anchor tag format (e.g., <a href="http://127.0.0.1:5000/customer/MEN">Link</a>) for products and categories** in the list items.
    Do NOT include API endpoints (e.g., /api/products/<id>).
    For queries about counts (e.g., number of product managers or products), provide the exact number and list relevant items in bullet points with their details and links.
    For filtered queries (e.g., products under $500), strictly filter items based on the context (e.g., price < 500) and list them with details (name, price, category) and their navigation link.
    Exclude any sensitive information like passwords.
    Use a professional yet engaging tone, like "Elevate your style with our latest collection!"
    If the query is unclear or no relevant data is found, suggest browsing products at <a href="/customer/clothes/ALL">All Products</a>.
    Context: {context}
    Query: {question}
    Answer:
    """

    prompt = PromptTemplate(template=prompt_template, input_variables=["question", "context"])

    # Set up RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 10}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    # Run the query
    result = qa_chain({"query": query})
    return result["result"], result["source_documents"]

if __name__ == "__main__":
    initialize_rag()