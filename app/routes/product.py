from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from ..models import User, Product, Order
from ..forms import ProductForm, DiscountForm
from ..models import Discount, DiscountType
from .. import db
from werkzeug.utils import secure_filename
import os

product_bp = Blueprint('product', __name__, url_prefix = '/product')

@product_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if not current_user.is_authenticated or current_user.role_id != 2:
        return redirect(url_for('main.home'))
    product_count = Product.query.filter_by(created_by=current_user.id, is_active=True).count()
    products = Product.query.filter_by(created_by=current_user.id,is_active=True).all()
    discounts = Discount.query.filter_by(created_by=current_user.id,is_active=True).all()
    return render_template('product/dashboard.html', product_count = product_count,products = products,discounts = discounts,title='product')

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