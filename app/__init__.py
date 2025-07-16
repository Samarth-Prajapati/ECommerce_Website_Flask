from flask import Flask, render_template, session, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from .config import Config
import pymysql
from .passwordHash import generate_password_hash, check_password_hash
from .forms import LoginForm, RegisterForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from authlib.integrations.flask_client import OAuth
import stripe

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

# Login Manager 
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Initialize OAuth
oauth = OAuth(app)

# Configure OAuth Providers
oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

oauth.register(
    name='github',
    client_id=app.config['GITHUB_CLIENT_ID'],
    client_secret=app.config['GITHUB_CLIENT_SECRET'],
    api_base_url='https://api.github.com/',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    client_kwargs={'scope': 'user:email'}
)

# Stripe Payment Configuration
stripe.api_key = app.config['STRIPE_SECRET_KEY']
stripe_publishable_key = app.config['STRIPE_PUBLISHABLE_KEY']

# Importing models for Initialization of Tables
from .models import Role, User, Category, Product, CartItem, Discount, Order, OrderItem, Invoice, Review, Report 

# Loading user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

with app.app_context():
    try:
        db.create_all() 
    except Exception as e:
        print(f"Error creating database tables: {e}")

from .routes import register_blueprints

# Registering Blueprints
register_blueprints(app)
