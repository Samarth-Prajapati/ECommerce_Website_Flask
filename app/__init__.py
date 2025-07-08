from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from .config import Config
import pymysql
from .passwordHash import generate_password_hash, check_password_hash

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
from .models import Role, User, Category, Product, CartItem, Discount, Order, OrderItem, Invoice, Review, Report 

with app.app_context():
    try:
        db.create_all() 
    except Exception as e:
        print(f"Error creating database tables: {e}")

@app.route('/')
def home():

    # SuperUser  
    # user = User(
    #         fname='SUPERUSER',
    #         lname='ADMIN',
    #         gender='MALE',
    #         email='superuser.admin@gmail.com',
    #         password=generate_password_hash('SUPERUSER'),
    #         contact='9876543210',
    #         address='ATUL',
    #         city='VALSAD',
    #         state='GUJARAT',
    #         role_id=1, 
    #     )
    # db.session.add(user)
    # db.session.commit()
    return render_template('home.html')

