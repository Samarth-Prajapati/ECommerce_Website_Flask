from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from ..forms import RegisterForm
from ..models import User
from .. import db
from .. passwordHash import generate_password_hash, check_password_hash

admin_bp = Blueprint('admin', __name__, url_prefix = '/admin')

@admin_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if not current_user.is_authenticated or current_user.role_id != 1:
        return redirect(url_for('main.home'))
    return render_template('admin/dashboard.html', title='admin')

# Add Product Manager  
@admin_bp.route('/dashboard/add_product_manager', methods=['GET', 'POST'])
@login_required
def add_product_manager():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        if User.query.filter_by(email=email).first():
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