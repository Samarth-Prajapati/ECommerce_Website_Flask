Shopify E-Commerce Platform with Chatbot
Welcome to Shopify, a robust Flask-based e-commerce platform designed to elevate your shopping experience with stylish collections for men, women, and kids! Powered by Samarth, our intelligent Retrieval-Augmented Generation (RAG) chatbot, this platform offers seamless product browsing, cart management, secure payments, and personalized assistance in a calm, polite tone. Samarth answers queries about products, discounts, and navigation, providing links to buy or view items for a user-friendly experience.
Features

User Roles: Admin, Product Manager, and Customer roles with tailored functionalities.
Product Management: Browse, filter, and add products to cart, apply discounts, and view order history.
Authentication: Secure login/register via email or OAuth (Google, GitHub).
Payment Integration: Process payments securely with Stripe.
Samarth Chatbot: Answers queries using data from files and MySQL, with real-time product filtering and links (e.g., /customer/product/t-shirt or /customer/clothes/MEN).
Responsive UI: Modern, Bootstrap-based design with a precise, live chat interface for Samarth.
Data Filtering: Efficiently retrieves relevant data, excluding sensitive information (e.g., IDs, passwords).

Prerequisites

Python: 3.8 or higher
MySQL: 8.0 or higher
Groq API Key: Obtain from https://console.groq.com/
Git: For cloning the repository
pip: For installing dependencies

Installation
Follow these steps to set up and run the Shopify platform with Samarth:

Create and Activate a Virtual Environment:
pip install virtualenv
virtualenv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

Install Dependencies:
pip install -r requirements.txt

Create a .env File:

In the project root (shopify_ecommerce/), create a .env file with the following template:MYSQL_HOST=localhost
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_PASSWORD_RAG=your_mysql_password_rag
MYSQL_DB=ecommerce_website
SECRET_KEY=your_flask_secret_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_SECRET_KEY=your_stripe_secret_key
MAIL_SERVER=smtp.yourmailserver.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email_username
MAIL_PASSWORD=your_email_password
MAIL_DEFAULT_SENDER=your_email_address
GROQ_API_KEY=your_groq_api_key

Replace placeholders with your actual credentials, obtained from respective services (e.g., MySQL, Google, GitHub, Stripe, Groq).

Set Up MySQL Database:

Ensure MySQL is running and create a database named shopify_db:CREATE DATABASE ecommerce_website;

The Flask app automatically initializes tables (products, categories, discounts, roles) on first run.

Create a superuser manually

Extract Data for Samarth:

Run the data extraction script to collect data from files (HTML, Python, JS, CSS) and MySQL:python app/utils/extract_data.py

This generates extracted_data.txt with product details, categories, discounts, and UI text, excluding sensitive fields like IDs.

Build FAISS Vector Store for Samarth:

Run the RAG setup script to create the vector store for retrieval:python app/utils/rag_chatbot.py

This creates the faiss_index/ directory, enabling Samarth to retrieve relevant data quickly.

Run the Application:

Start the Flask app:python run.py

Access the platform at http://127.0.0.1:5000.

Usage

Explore the Website:

Visit http://127.0.0.1:5000 to browse products, manage your cart, apply discounts, and update your profile.
Use the navigation bar to access features like “Products” or “Chat with Samarth.”

Chat with Samarth:

Navigate to http://127.0.0.1:5000/chatbot for a live chat interface.
Ask questions like:
“Show me products in the MEN category.”
“How do I apply a discount?”
“What roles are available?”

Samarth responds politely with detailed answers, including links to buy products (e.g., /customer/product/t-shirt) or view categories (e.g., /customer/clothes/MEN).
Example Response:
Hello [Your Name], I’m Samarth, here to assist you calmly! In the MEN category, you can find:

T-Shirt: Comfortable cotton shirt, $19.99. Buy Now
Jeans: Classic fit, $49.99. Buy NowExplore more at /customer/clothes/MEN. Happy shopping!

Update Data:

If products, discounts, or files change, rerun:python app/utils/extract_data.py
python app/utils/rag_chatbot.py

Automate updates with a cron job:0 0 \* \* \* /path/to/python /path/to/shopify_ecommerce/app/utils/extract_data.py && /path/to/python /path/to/shopify_ecommerce/app/utils/rag_chatbot.py

Data Sources and Filtering

Files: Extracts user-facing text from HTML (e.g., “Shop Now” from home.html), flash messages from Python (e.g., “Product Added to Cart…”), and comments from JS/CSS using BeautifulSoup.
MySQL: Queries active records from products, categories, discounts, and roles, excluding sensitive fields (e.g., IDs). Includes product and category URLs for linking.
Filtering: Samarth uses FAISS to retrieve the top 5 relevant text chunks based on semantic similarity, ensuring accurate responses. For filtered queries (e.g., “MEN products”), it provides links to relevant product or category pages.

Project Structure
shopify_ecommerce/
├── app/
│ ├── **init**.py
│ ├── routes.py
│ ├── auth.py
│ ├── main.py
│ ├── admin.py
│ ├── user_profile.py
│ ├── product.py
│ ├── customer.py
│ ├── chatbot.py
│ ├── utils/
│ │ ├── extract_data.py
│ │ ├── rag_chatbot.py
│ ├── models.py
│ ├── forms.py
│ ├── passwordHash.py
├── templates/
│ ├── base.html
│ ├── home.html
│ ├── completeProfile.html
│ ├── show.html
│ ├── update.html
│ ├── order_history.html
│ ├── product_details.html
│ ├── cart.html
│ ├── add_product.html
│ ├── discount.html
│ ├── clothes.html
│ ├── dashboard.html
│ ├── add_product_manager.html
│ ├── edit.html
│ ├── chatbot.html
├── static/
│ ├── scripts.js
│ ├── style.css
│ ├── reports/
├── extracted_data.txt
├── faiss_index/
├── .env
├── requirements.txt
├── app.py

Troubleshooting

MySQL Connection:
Verify .env credentials and MySQL server status.
Test connectivity:import pymysql
from dotenv import load_dotenv
import os
load_dotenv()
conn = pymysql.connect(
host=os.getenv("MYSQL_HOST"),
user=os.getenv("MYSQL_USER"),
password=os.getenv("MYSQL_PASSWORD"),
database=os.getenv("MYSQL_DB")
)
print("Connected!")
conn.close()

Samarth Issues:
Ensure extracted_data.txt and faiss_index/ exist.
Verify GROQ_API_KEY in .env.
Rerun extract_data.py and rag_chatbot.py if data is outdated.

Dependencies:
Run pip install -r requirements.txt to resolve missing packages.

UI Issues:
Clear browser cache if the chatbot interface doesn’t render correctly.

Contributing
We welcome contributions to enhance Samarth or the Shopify platform! Submit pull requests or open issues on GitHub.
License
This project is licensed under the MIT License. See the LICENSE file for details.

Shopify & Samarth: Elevate your style and shop smarter! Chat with Samarth for instant, polite assistance or explore our collections today!
