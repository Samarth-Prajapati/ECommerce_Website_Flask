from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from ..forms import LoginForm, RegisterForm
from ..models import User
from .. import db
from .. passwordHash import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix = '/auth')

# Login 
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You Are Already Logged In...', 'info')
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=False)
            flash('Login Successful...', 'success')
            if user.role_id == 1:
                return redirect(url_for('main.home'))
            elif user.role_id == 2:
                return redirect(url_for('main.home'))
            return redirect(url_for('main.home'))
        else:
            flash('Invalid Email or Password', 'danger')
    return render_template('login.html', form=form, title='Login')

# Register  
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You Are Already Logged In...', 'info')
        return redirect(url_for('main.home'))
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        if User.query.filter_by(email=email).first():
            flash('Email Already Registered...', 'danger')
            return render_template('register.html', form=form, title='Register')
        if User.query.filter_by(password=generate_password_hash(password)).first():
            flash('Password Already Used...', 'danger')
            return render_template('register.html', form=form, title='Register')
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
            role_id=3,  
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration Successful! Please Log In...', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form, title='Register')

# Logout 
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged Out Successfully...', 'success')
    return redirect(url_for('auth.login'))

