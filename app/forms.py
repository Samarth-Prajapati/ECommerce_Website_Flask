from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, FloatField, IntegerField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, Optional, URL, NumberRange, ValidationError

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

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(min=2, max=150)])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0.01)])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    available = BooleanField('Available', default=True)
    image_url = StringField('Product Image URL', validators=[Optional(), URL(message="Please enter a valid URL")])
    category_id = SelectField('Category', coerce=int, choices=[(1, 'MEN'), (2, 'WOMEN'), (3, 'KIDS')], validators=[DataRequired()])
    submit = SubmitField('Add Product')

class AddToCartForm(FlaskForm):
    submit = SubmitField('Add to Cart')

class ReviewForm(FlaskForm):
    product_id = HiddenField('Product ID', validators=[DataRequired()])
    rating = SelectField('Rating', choices=[(i, str(i)) for i in range(1, 6)], coerce=int, validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Submit Review')

class DiscountForm(FlaskForm):
    name = StringField('Discount Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    discount_type = SelectField(
        'Discount Type',
        choices=[('FLAT', 'FLAT'), ('PERCENT', 'PERCENT')],  
        validators=[DataRequired()]
    )
    value = FloatField('Discount Value', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Create Discount')