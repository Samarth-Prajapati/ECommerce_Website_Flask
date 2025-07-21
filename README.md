1. create a virtualenv and activate
2. pip install -r requirements.txt
3. create .env file
   MYSQL_HOST
   MYSQL_USER
   MYSQL_PASSWORD
   MYSQL_PASSWORD_RAG
   MYSQL_DB
   SECRET_KEY
   GOOGLE_CLIENT_ID
   GOOGLE_CLIENT_SECRET
   GITHUB_CLIENT_ID
   GITHUB_CLIENT_SECRET
   STRIPE_PUBLISHABLE_KEY
   STRIPE_SECRET_KEY
   MAIL_SERVER
   MAIL_PORT
   MAIL_USE_TLS
   MAIL_USERNAME
   MAIL_PASSWORD
   MAIL_DEFAULT_SENDER
   GROQ_API_KEY
4. python app/utils/extract_data.py
5. python app/utils/rag_chatbot.py
6. python run.py
