from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Step 1: Load and split the extracted data
loader = TextLoader("extracted_data.txt", encoding="utf-8")
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)
docs = text_splitter.split_documents(documents)

# Step 2: Create embeddings and store in FAISS
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(docs, embeddings)
vectorstore.save_local("faiss_index")

# Step 3: Set up the Groq LLM
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama3-8b-8192",
    temperature=0.7,
    max_tokens=512
)

# Step 4: Create the RAG chain
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a helpful chatbot for the Shopify e-commerce website, designed to assist users with information about the platform. Answer all questions accurately based on the provided context, using a professional yet friendly tone that aligns with the website's style (e.g., "Elevate your style with our latest collection" or "Product Added to Cart..."). If the context doesn't provide enough information to answer a question, respond politely that you don't have sufficient details but offer to assist with something else. Always aim to be concise, informative, and engaging.

Context: {context}

Question: {question}

Answer:
"""
)

# Now use this PromptTemplate inside chain_type_kwargs
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt_template}
)

def get_chatbot_response(query):
    """Function to get a response from the chatbot."""
    result = qa_chain({"query": query})
    return result["result"], result["source_documents"]