from app import db
from datetime import datetime
import enum
from flask_login import UserMixin

# Enum for gender
class Gender(enum.Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    OTHERS = 'OTHERS'

# Enum for discount_type
class DiscountType(enum.Enum):
    FLAT = 'FLAT'
    PERCENT = 'PERCENT'

# Enum for order status
class OrderStatus(enum.Enum):
    PENDING = 'PENDING'
    SUCCESS = 'SUCCESS'
    CANCELED = 'CANCELED'

# Enum for report type
class ReportType(enum.Enum):
    PRODUCT_REPORT = 'PRODUCT_REPORT'
    USER_REPORT = 'USER_REPORT'

# Role DB Model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy=True)

# User DB Model
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.Enum(Gender), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), default = 3, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.relationship('Product', backref='creator', lazy=True)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    reports = db.relationship('Report', backref='generator', lazy=True)

# Category DB Model
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

# Product DB Model
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    available = db.Column(db.Boolean, default=True)
    image = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True)

# CartItem DB Model
class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    product_status = db.Column(db.Boolean, default=True)

# Discount DB Model
class Discount(db.Model):
    __tablename__ = 'discounts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    discount_type = db.Column(db.Enum(DiscountType), nullable=False)
    value = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='discount', lazy=True)

# Order DB Model
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    invoice = db.Column(db.String(255), nullable=False)
    payment_id = db.Column(db.String(100), nullable=False)
    discount_id = db.Column(db.Integer, db.ForeignKey('discounts.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    order_items = db.relationship('OrderItem', backref='order', lazy=True)
    invoice_record = db.relationship('Invoice', backref='order', uselist=False, lazy=True)

# OrderItem DB Model
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

# Invoice DB Model
class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), unique=True, nullable=False)
    gst_percent = db.Column(db.Float, nullable=False)
    total_before_tax = db.Column(db.Float, nullable=False)
    total_gst = db.Column(db.Float, nullable=False)
    total_after_tax = db.Column(db.Float, nullable=False)
    pdf_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Review DB Model
class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.CheckConstraint('rating >= 1 AND rating <= 5', name='rating_range'),)

# Report DB Model
class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    generated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    report_type = db.Column(db.Enum(ReportType), nullable=False)
    format = db.Column(db.String(10), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)