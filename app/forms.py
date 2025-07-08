from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Log In')

class RegisterForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired(), Length(max=100), Regexp(r'^[A-Za-z\s]+$', message='First name must contain only letters and spaces')])
    lname = StringField('Last Name', validators=[DataRequired(), Length(max=100), Regexp(r'^[A-Za-z\s]+$', message='Last name must contain only letters and spaces')])
    gender = SelectField('Gender', choices=[('MALE', 'MALE'), ('FEMALE', 'FEMALE'), ('OTHERS', 'OTHERS')], validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=255)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    contact = StringField('Contact', validators=[DataRequired(), Length(max=20), Regexp(r'^\+?[0-9\s\-]+$', message='Invalid contact number')])
    address = TextAreaField('Address', validators=[DataRequired(), Length(max=1000)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    state = StringField('State', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Register')