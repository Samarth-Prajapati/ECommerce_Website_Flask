from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from ..models import User, Product, Order
from ..forms import ProductForm
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
    return render_template('product/dashboard.html', product_count = product_count,title='product')

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