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
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        if User.query.filter_by(email=email).first():
            flash('Email Already Registered...', 'register_pm')
            return render_template('admin/dashboard.html', form=form, title='admin')
        if User.query.filter_by(password=generate_password_hash(password)).first():
            flash('Password Already Used...', 'register_pm')
            return render_template('admin/dashboard.html', form=form, title='admin')
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
        flash('Registration Successful...', 'register_pm')
    return render_template('admin/dashboard.html', form = form,title='admin')
