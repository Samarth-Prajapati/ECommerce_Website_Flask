from flask import Blueprint, redirect, url_for, flash, render_template, request
from flask_login import login_required, current_user
from ..passwordHash import generate_password_hash
from .. import db
from ..models import User
from ..forms import RegisterForm

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/show')
@login_required
def show():
    if not current_user.is_authenticated:
        flash('Please Login...', 'profile')
        return redirect(url_for('main.home'))
    profile_data = current_user
    return render_template('user_profile/show.html', profile_data = profile_data, title='show')

@profile_bp.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    formR = RegisterForm()
    if not current_user.is_authenticated:
        flash('Please Login...', 'profile')
        return redirect(url_for('main.home'))
    profile_data = current_user
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash('Passwords Do Not Match...', 'profile')
            return redirect(url_for('profile.update'))
        current_user.password = generate_password_hash(password)
        current_user.contact = request.form.get('contact')
        current_user.address = request.form.get('address').upper()
        current_user.city = request.form.get('city').upper()
        current_user.state = request.form.get('state').upper()
        db.session.commit() 
        flash('Profile Updated Successfully...', 'profile')
        return redirect(url_for('profile.show'))
    return render_template('user_profile/update.html', profile_data = profile_data, form = formR,title='update')