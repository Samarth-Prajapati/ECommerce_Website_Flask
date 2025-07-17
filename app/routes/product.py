from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory
from flask_login import current_user, login_required
from ..models import User, Product, Order, Order, Review, Category, Report, ReportType
from sqlalchemy import func
from ..forms import ProductForm, DiscountForm
from ..models import Discount, DiscountType, OrderItem, OrderStatus
from sqlalchemy.orm import joinedload, load_only
from .. import db
from werkzeug.utils import secure_filename
import os
import pandas as pd
from flask import current_app
from datetime import datetime
from ..utils.email_utils import send_report_email

product_bp = Blueprint('product', __name__, url_prefix = '/product')

@product_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if not current_user.is_authenticated or current_user.role_id != 2:
        return redirect(url_for('main.home'))
    product_count = Product.query.filter_by(created_by=current_user.id, is_active=True).count()
    products = Product.query.filter_by(created_by=current_user.id,is_active=True).all()
    discounts = Discount.query.filter_by(created_by=current_user.id,is_active=True).all()
    orders = db.session.query(Order)\
        .join(OrderItem, Order.id == OrderItem.order_id)\
        .join(Product, Product.id == OrderItem.product_id)\
        .filter(Product.created_by == current_user.id)\
        .filter(Order.status == OrderStatus.SUCCESS)\
        .options(joinedload(Order.user))\
        .distinct()\
        .all()
    return render_template('product/dashboard.html', product_count = product_count,products = products,discounts = discounts,orders=orders,title='product')

# Add Product Manager  
@product_bp.route('/dashboard/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            quantity=form.quantity.data,
            available=form.available.data,
            image=form.image_url.data,  
            category_id=form.category_id.data,
            created_by=current_user.id,
            is_active=True
        )
        db.session.add(product)
        db.session.commit()
        flash('Product Added Successfully...', 'product')
        return redirect(url_for('product.dashboard'))
    return render_template('product/add_product.html', form=form, title='add_product')


# Update 
@product_bp.route('/dashboard/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    if not current_user.is_authenticated or current_user.role_id != 2:
        flash('Please Login...', 'login')
        return redirect(url_for('main.home'))
    product = Product.query.get_or_404(id)
    form = ProductForm()
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = request.form.get('price')
        product.quantity = request.form.get('quantity')
        product.image = request.form.get('image')
        product.available = 'available' in request.form
        db.session.commit() 
        flash('Updated Successfully...', 'product')
        return redirect(url_for('product.dashboard'))
    return render_template('product/update.html', product=product, form=form, title='update')

# Delete 
@product_bp.route('/dashboard/delete/<int:id>', methods=['GET'])
@login_required
def delete(id):
    if not current_user.is_authenticated or current_user.role_id != 2:
        return redirect(url_for('main.home'))
    product = Product.query.get_or_404(id)
    product.is_active = False
    db.session.commit()
    flash('Product Deleted Successfully...', 'delete')
    return redirect(url_for('product.dashboard'))

# Discount
@product_bp.route('/dashboard/discount', methods=['GET','POST'])
@login_required
def discount():
    if not current_user.is_authenticated or current_user.role_id != 2:
        flash('Please Login...', 'login')
        return redirect(url_for('main.home'))
    form = DiscountForm()
    if form.validate_on_submit():
        new_discount = Discount(
            name=form.name.data.upper(),
            description=form.description.data.upper(),
            discount_type=DiscountType[form.discount_type.data], 
            value=form.value.data,
            created_by=current_user.id
        )
        db.session.add(new_discount)
        db.session.commit()
        flash('Discount created successfully!', 'product')
        return redirect(url_for('product.dashboard')) 
    return render_template('product/discount.html', form=form, title='discount')

# Delete Discount
@product_bp.route('/dashboard/delete-discount/<int:id>', methods=['GET'])
@login_required
def deleteDiscount(id):
    if not current_user.is_authenticated or current_user.role_id != 2:
        return redirect(url_for('main.home'))
    discount = Discount.query.filter_by(id=id, created_by=current_user.id).first_or_404()
    discount.is_active = False
    db.session.commit()
    flash('Discount Deleted Successfully...', 'delete')
    return redirect(url_for('product.dashboard'))

@product_bp.route('/download/product-report', methods=['GET'])
@login_required
def download_product_report():
    if not current_user.is_authenticated or current_user.role_id != 1:
        flash("Access denied!", "login")
        return redirect(url_for("main.home"))
    report_folder = os.path.join(current_app.root_path, "static", "reports")
    os.makedirs(report_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"product_report_{timestamp}.csv"
    filepath = os.path.join(report_folder, filename)
    products = Product.query.options(joinedload(Product.category)).all()
    data = []
    for product in products:
        reviews = Review.query.filter_by(product_id=product.id, is_active=True).all()
        total_reviews = len(reviews)
        avg_rating = round(sum([r.rating for r in reviews]) / total_reviews, 2) if total_reviews else 0
        units_sold = db.session.query(func.coalesce(func.sum(OrderItem.quantity), 0))\
            .join(Order)\
            .filter(OrderItem.product_id == product.id)\
            .filter(Order.status == OrderStatus.SUCCESS)\
            .scalar()
        customer_query = db.session.query(User.fname, User.lname)\
            .join(Order, Order.user_id == User.id)\
            .join(OrderItem, OrderItem.order_id == Order.id)\
            .filter(OrderItem.product_id == product.id)\
            .filter(Order.status == OrderStatus.SUCCESS)\
            .distinct()\
            .all()
        total_customers = len(customer_query)
        customer_names = ", ".join([f"{fname} {lname}" for fname, lname in customer_query]) or "N/A"
        data.append({
            "Product Name": product.name,
            "Description": product.description,
            "Price": product.price,
            "Quantity": product.quantity,
            "Available": "Yes" if product.available else "No",
            "Image": product.image or "N/A",
            "Category ID": product.category_id,
            "Created By (User ID)": product.created_by,
            "Is Active": "Yes" if product.is_active else "No",
            "Created At": product.created_at.strftime('%Y-%m-%d'),
            "Total Reviews": total_reviews,
            "Average Rating": avg_rating,
            "Units Sold": units_sold,
            "Total Customers": total_customers,
            "Customer Names": customer_names
        })
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)
    report = Report(
        generated_by=current_user.id,
        report_type=ReportType.PRODUCT_REPORT,
        format='csv',
        file_path=f"reports/{filename}"
    )
    db.session.add(report)
    db.session.commit()
    absolute_path = os.path.join(report_folder, filename)
    send_report_email(
        recipient_email='samarthp475@gmail.com', 
        subject="📦 Your Product Report CSV",
        body="Attached is the latest product report you requested.",
        attachment_path=absolute_path
    )
    return redirect(url_for('product.serve_report_file', filename=filename))


@product_bp.route('/download/user-report', methods=['GET'])
@login_required
def download_user_report():
    if not current_user.is_authenticated or current_user.role_id != 1:
        flash("Access denied!", "login")
        return redirect(url_for("main.home"))
    folder = os.path.join(current_app.root_path, "static", "reports")
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"user_report_{timestamp}.csv"
    filepath = os.path.join(folder, filename)
    users = User.query.options(
        joinedload(User.products),
        joinedload(User.role)
    ).all()
    data = []
    for idx, user in enumerate(users):
        user_data = {
            "#": idx + 1,
            "Name": f"{user.fname} {user.lname}",
            "Email": user.email,
            "Role": user.role.name if user.role else "N/A",
            "Registered On": user.created_at.strftime('%Y-%m-%d'),
            "Total Products": "",
            "Total Units Sold": "",
            "Products": "",
            "Products Bought": "",
            "Total Spent": "",
        }

        if user.role.name == "PRODUCT MANAGER":
            products = user.products
            user_data["Total Products"] = len(products)
            total_sold = 0
            product_details = []
            for product in products:
                sold_units = db.session.query(func.coalesce(func.sum(OrderItem.quantity), 0))\
                    .join(Order, Order.id == OrderItem.order_id)\
                    .filter(Order.status == OrderStatus.SUCCESS)\
                    .filter(OrderItem.product_id == product.id)\
                    .scalar() or 0
                total_sold += sold_units
                product_details.append(f"{product.name} (Sold: {sold_units})")
            user_data["Total Units Sold"] = total_sold
            user_data["Products"] = "; ".join(product_details) or "None"
        elif user.role.name == "CUSTOMER":
            orders = Order.query.filter_by(user_id=user.id, status=OrderStatus.SUCCESS).all()
            bought_products = []
            total_spent = 0
            for order in orders:
                for item in order.order_items:
                    if item.product:
                        bought_products.append(f"{item.product.name} (Qty: {item.quantity})")
                        total_spent += item.price * item.quantity
            user_data["Products Bought"] = ", ".join(bought_products) or "None"
            user_data["Total Spent"] = f"${total_spent:.2f}"
        data.append(user_data)
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)
    report = Report(
        generated_by=current_user.id,
        report_type=ReportType.USER_REPORT,
        format='csv',
        file_path=f"reports/{filename}"
    )
    db.session.add(report)
    db.session.commit()
    absolute_path = os.path.join(folder, filename)
    send_report_email(
        recipient_email='samarthp475@gmail.com',  
        subject="👤 Your User Report CSV",
        body="Attached is the latest user report you requested.",
        attachment_path=absolute_path
    )

    return redirect(url_for('product.serve_report_file', filename=filename))


@product_bp.route('/reports/<filename>', methods=['GET'])
@login_required
def serve_report_file(filename):
    report_folder = os.path.join(current_app.root_path, "static", "reports")
    return send_from_directory(report_folder, filename, as_attachment=True)

