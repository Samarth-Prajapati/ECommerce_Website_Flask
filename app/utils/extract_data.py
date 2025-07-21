import os
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
import pymysql.cursors

# Load environment variables
load_dotenv()
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD_RAG', 'Apple@2310') 
MYSQL_DB = os.getenv('MYSQL_DB', 'ECOMMERCE_WEBSITE')

def connect_to_db():
    """Connect to MySQL database using pymysql."""
    try:
        connection = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def extract_from_mysql():
    """Extract relevant data from MySQL tables."""
    connection = connect_to_db()
    if not connection:
        return []
    
    try:
        with connection.cursor() as cursor:
            # Extract products (only active products)
            cursor.execute("SELECT name, description, price, quantity, available, category_id FROM products WHERE is_active = 1")
            products = cursor.fetchall()
            product_data = [
                f"Product: {p['name']}, Description: {p['description']}, Price: ${p['price']}, Quantity: {p['quantity']}, Available: {p['available']}, Category ID: {p['category_id']}"
                for p in products
            ]
            
            # Extract categories
            cursor.execute("SELECT id, name FROM categories")
            categories = cursor.fetchall()
            category_data = [f"Category: {c['name']}, ID: {c['id']}" for c in categories]
            
            # Extract discounts (only active discounts)
            cursor.execute("SELECT name, description, discount_type, value FROM discounts WHERE is_active = 1")

            discounts = cursor.fetchall()
            discount_data = [
                f"Discount: {d['name']}, Description: {d['description']}, Type: {d['discount_type']}, Value: {d['value']}"
                for d in discounts
            ]
            
            # Extract user roles
            cursor.execute("SELECT id, name FROM roles")
            roles = cursor.fetchall()
            role_data = [f"Role: {r['name']}, ID: {r['id']}" for r in roles]
            
        return product_data + category_data + discount_data + role_data
    except Exception as e:
        print(f"Error extracting from MySQL: {e}")
        return []
    finally:
        connection.close()

def extract_text_from_html(file_path):
    """Extract text from HTML files, removing tags and scripts."""
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return ' '.join(chunk for chunk in chunks if chunk)

def extract_text_from_python(file_path):
    """Extract docstrings, comments, routes, and flash messages from Python files."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        docstrings = re.findall(r'"""(.*?)"""', content, re.DOTALL)
        comments = re.findall(r'#.*$', content, re.MULTILINE)
        routes = re.findall(r'@.*?\.route\(["\'](.*?)["\'].*?\n\s*def\s+(\w+)', content)
        flashes = re.findall(r'flash\(["\'](.*?)["\'].*?\)', content)
        return '\n'.join(docstrings + comments + [f"Route: {r[0]} Function: {r[1]}" for r in routes] + flashes)

def extract_text_from_js(file_path):
    """Extract comments from JS files."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        comments = re.findall(r'//.*$|/\*.*?\*/', content, re.DOTALL | re.MULTILINE)
        return '\n'.join(comments)

def extract_text_from_css(file_path):
    """Extract comments from CSS files."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        comments = re.findall(r'/\*.*?\*/', content, re.DOTALL)
        return '\n'.join(comments)

def extract_all_files(directory):
    """Extract text from all relevant files in the directory."""
    documents = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.html'):
                text = extract_text_from_html(file_path)
                documents.append(f"File: {file}\n{text}")
            elif file.endswith('.py'):
                text = extract_text_from_python(file_path)
                documents.append(f"File: {file}\n{text}")
            elif file.endswith('.js'):
                text = extract_text_from_js(file_path)
                documents.append(f"File: {file}\n{text}")
            elif file.endswith('.css'):
                text = extract_text_from_css(file_path)
                documents.append(f"File: {file}\n{text}")
    return documents

if __name__ == "__main__":
    directories = ['./templates', './app']
    all_docs = []

    for dir_path in directories:
        all_docs.extend(extract_all_files(dir_path))  # Pass one directory at a time

    all_docs.extend(extract_from_mysql())
    
    with open('extracted_data.txt', 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(all_docs))