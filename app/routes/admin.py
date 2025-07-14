from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from ..forms import RegisterForm
from ..models import User, Product
from .. import db
from .. passwordHash import generate_password_hash, check_password_hash

admin_bp = Blueprint('admin', __name__, url_prefix = '/admin')

@admin_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if not current_user.is_authenticated or current_user.role_id != 1:
        return redirect(url_for('main.home'))
    users = User.query.filter_by(is_active=True).filter(User.role_id != 1).all()
    productManager_count = User.query.filter_by(role_id=2, is_active=True).count()
    customer_count = User.query.filter_by(role_id=3, is_active=True).count()
    product_count = Product.query.count()
    return render_template('admin/dashboard.html',users = users, productManager_count = productManager_count, customer_count = customer_count, product_count = product_count, title='admin')

# Add Product Manager  
@admin_bp.route('/dashboard/add_product_manager', methods=['GET', 'POST'])
@login_required
def add_product_manager():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        if User.query.filter_by(email=email).first() and User.query.filter_by(email=email).first().is_active:
            flash('Email Already Registered...', 'add_product_manager')
            return render_template('admin/add_product_manager.html', form=form, title='add_product_manager')
        user = User(
            fname=form.fname.data.upper(),
            lname=form.lname.data.upper(),
            gender=form.gender.data,
            email=email,
            password=generate_password_hash(password),
            contact=form.contact.data,
            address=form.address.data.upper(),
            city=form.city.data.upper(),
            state=form.state.data.upper(),
            role_id=2,  
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration Successful...', 'register_pm1')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/add_product_manager.html', form=form, title='add_product_manager')

# Update 
@admin_bp.route('/dashboard/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    formR = RegisterForm()
    if not current_user.is_authenticated:
        flash('Please Login...', 'profile')
        return redirect(url_for('main.home'))
    profile_data = User.query.get_or_404(id)
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash('Passwords Do Not Match...', 'edit')
            return redirect(url_for('admin.edit', id=id))
        profile_data.password = generate_password_hash(password)
        profile_data.contact = request.form.get('contact')
        profile_data.address = request.form.get('address').upper()
        profile_data.city = request.form.get('city').upper()
        profile_data.state = request.form.get('state').upper()
        db.session.commit() 
        flash('Profile Updated Successfully...', 'register_pm1')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit.html', profile_data = profile_data, form = formR,title='edit')

# Delete 
@admin_bp.route('/dashboard/delete/<int:id>', methods=['GET'])
@login_required
def delete(id):
    if not current_user.is_authenticated or current_user.role_id != 1:
        return redirect(url_for('main.home'))
    user = User.query.get_or_404(id)
    if user.role_id == 1:
        flash('Cannot Deactivate Admin User', 'delete')
        return redirect(url_for('admin.dashboard'))
    else:
        user.is_active = False
        db.session.commit()
        flash('User Deleted Successfully...', 'delete')
    return redirect(url_for('admin.dashboard'))
