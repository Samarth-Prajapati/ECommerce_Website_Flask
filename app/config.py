from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'Apple%402310') 
    MYSQL_DB = os.getenv('MYSQL_DB', 'ECOMMERCE_WEBSITE')
    SECRET_KEY = os.getenv('SECRET_KEY', '1234567890abcdefewtwr4')
    SESSION_PERMANENT = False  
    WTF_CSRF_ENABLED = True