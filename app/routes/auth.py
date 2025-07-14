from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from ..forms import LoginForm, RegisterForm
from ..models import User
from .. import db, oauth
from .. passwordHash import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix = '/auth')

# Login 
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You Are Already Logged In...', 'login')
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and (user.oauth_provider or check_password_hash(user.password, password)):
            login_user(user, remember=False)
            flash('Login Successful...', 'login')
            if user.role_id == 1:
                return redirect(url_for('main.home'))
            elif user.role_id == 2:
                return redirect(url_for('main.home'))
            return redirect(url_for('main.home'))
        else:
            flash('Invalid Email or Password', 'login1')
    return render_template('login.html', form=form, title='Login')

# Register  
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You Are Already Logged In...', 'register')
        return redirect(url_for('main.home'))
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        if User.query.filter_by(email=email, is_active = True).first():
                flash('Email Already Registered...', 'register1')
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
        flash('Registration Successful! Please Log In...', 'register')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form, title='Register')

# Logout 
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged Out Successfully...', 'logout')
    return redirect(url_for('auth.login'))

@auth_bp.route('/login/google')
def google_login():
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/callback/google')
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        user_info = oauth.google.parse_id_token(token, nonce=None)
        email = user_info.get('email')
        oauth_id = user_info.get('sub')
        fname = user_info.get('given_name', 'User')
        lname = user_info.get('family_name', 'Google')
        username = email.split('@')[0]
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                fname=fname.upper(),
                lname=lname.upper(),
                email=email,
                oauth_provider='google',
                oauth_id=oauth_id,
                role_id=3,
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Please Complete Your Profile...', 'oauth')
            return redirect(url_for('auth.complete_profile'))
        elif user.oauth_provider != 'google' or user.oauth_id != oauth_id:
            user.oauth_provider = 'google'
            user.oauth_id = oauth_id
            user.fname = fname.upper()
            user.lname = lname.upper()
            db.session.commit()
        elif User.query.filter_by(email=email, is_active=False).first():
            user = User(
                fname=fname.upper(),
                lname=lname.upper(),
                email=email,
                oauth_provider='google',
                oauth_id=oauth_id,
                role_id=3,
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Please Complete Your Profile...', 'oauth')
            return redirect(url_for('auth.complete_profile'))
        login_user(user)
        flash('Logged In With Google...', 'oauth')
        return redirect(url_for('main.home'))
    except Exception as e:
        flash(f'Google Login Failed: {str(e)}', 'oauth')
        return redirect(url_for('auth.login'))

@auth_bp.route('/login/github')
def github_login():
    redirect_uri = url_for('auth.github_callback', _external=True)
    return oauth.github.authorize_redirect(redirect_uri)

@auth_bp.route('/callback/github')
def github_callback():
    try:
        token = oauth.github.authorize_access_token()
        resp = oauth.github.get('user').json()
        email_resp = oauth.github.get('user/emails').json()
        email = next((e['email'] for e in email_resp if e['primary'] and e['verified']), None)
        if not email:
            flash('GitHub Email Not Available Or Not Verified...', 'oauth')
            return redirect(url_for('auth.login'))
        oauth_id = str(resp.get('id'))
        fname = resp.get('name', 'User').split(' ')[0]
        lname = ' '.join(resp.get('name', 'GitHub').split(' ')[1:]) if resp.get('name') and len(resp.get('name').split()) > 1 else 'GitHub'
        username = resp.get('login')
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                fname=fname.upper(),
                lname=lname.upper(),
                email=email,
                oauth_provider='github',
                oauth_id=oauth_id,
                role_id=3,
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Please Complete Your Profile...', 'oauth')
            return redirect(url_for('auth.complete_profile'))
        elif user.oauth_provider != 'github' or user.oauth_id != oauth_id:
            user.oauth_provider = 'github'
            user.oauth_id = oauth_id
            user.fname = fname.upper()
            user.lname = lname.upper()
            db.session.commit()
        elif User.query.filter_by(email=email, is_active=False).first():
            user = User(
                fname=fname.upper(),
                lname=lname.upper(),
                email=email,
                oauth_provider='github',
                oauth_id=oauth_id,
                role_id=3,
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Please Complete Your Profile...', 'oauth')
            return redirect(url_for('auth.complete_profile'))
        login_user(user)
        flash('Logged In With GitHub...', 'oauth')
        return redirect(url_for('main.home'))
    except Exception as e:
        flash(f'GitHub Login Failed: {str(e)}', 'oauth')
        return redirect(url_for('auth.login'))

@auth_bp.route('/complete_profile', methods=['GET', 'POST'])
@login_required
def complete_profile():
    form = RegisterForm()
    if request.method == 'POST':
        if not form.validate():
            flash('Please Correct The Errors In The Form...', 'oauth')
            return render_template('completeProfile.html', form=form, title='complete_profile')
        email = form.email.data
        if db.session.query(User).filter_by(email=email).first() and email != current_user.email:
            flash('Email Already In Use...', 'oauth')
            return render_template('completeProfile.html', form=form, title='complete_profile')
        if form.password.data:
            if form.password.data != form.confirm_password.data:
                flash('Passwords Do Not Match...', 'oauth')
                return render_template('completeProfile.html', form=form, title='complete_profile')
        try:
            current_user.email = email
            current_user.fname = form.fname.data.upper()
            current_user.lname = form.lname.data.upper()
            current_user.gender = form.gender.data
            current_user.contact = form.contact.data
            current_user.address = form.address.data.upper()
            current_user.city = form.city.data.upper()
            current_user.state = form.state.data.upper()
            if form.password.data:
                current_user.password = generate_password_hash(form.password.data)
            db.session.commit()
            flash('Profile Updated Successfully...', 'oauth')
            return redirect(url_for('main.home'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error Updating Profile: {str(e)}', 'oauth')
            return render_template('completeProfile.html', form=form, title='complete_profile')
    form.fname.data = current_user.fname or ''
    form.lname.data = current_user.lname or ''
    form.email.data = current_user.email or ''
    form.gender.data = current_user.gender or 'MALE'  
    form.contact.data = current_user.contact or ''
    form.address.data = current_user.address or ''
    form.city.data = current_user.city or ''
    form.state.data = current_user.state or ''
    return render_template('completeProfile.html', form=form, title='complete_profile')