from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
import pymysql

app = Flask(__name__)

# Loading Configration
app.config.from_object(Config)

user = app.config['MYSQL_USER']
password = app.config['MYSQL_PASSWORD']
host = app.config['MYSQL_HOST']
database = app.config['MYSQL_DB']

# Configuring SQLAlchemy - MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{password}@{host}/{database}'

# Initializing SQLAlchemy
db = SQLAlchemy(app)

# Importing models for Initialization of Tables
# from .models import  

with app.app_context():
    db.create_all() 

@app.route('/')
def home():
    return 'Home Page'

