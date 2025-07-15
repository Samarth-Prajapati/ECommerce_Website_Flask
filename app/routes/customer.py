from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models import Product, User, Category, CartItem, Review
from flask_login import login_required, current_user
from .. import db
from ..forms import AddToCartForm, ReviewForm

customer_bp = Blueprint('customer', __name__, url_prefix = '/customer')

@customer_bp.route('/<category_name>', methods=['GET', 'POST'])
def clothes(category_name):
    search_query = request.args.get('search', '').strip()
    if category_name == 'ALL':
        products = Product.query.filter_by(is_active=True)\
            .join(User, Product.created_by == User.id)\
            .join(Category, Product.category_id == Category.id)\
            .all()
    else:
        category_name = category_name.upper()
        products = Product.query.filter_by(is_active=True)\
        .join(User, Product.created_by == User.id)\
        .join(Category, Product.category_id == Category.id)\
        .filter(Category.name == category_name)\
        .all()
    return render_template('product/clothes.html',products=products,category_name = category_name ,title='clothes')

@customer_bp.route('/product/<int:product_id>', methods=['GET'])
def product_details(product_id):
    product = Product.query.filter_by(id=product_id, is_active=True)\
        .join(User, Product.created_by == User.id)\
        .join(Category, Product.category_id == Category.id)\
        .first_or_404()
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id, product_status=True).first() if current_user.is_authenticated else None
    form = AddToCartForm()
    review_form = ReviewForm()
    reviews = Review.query.filter_by(product_id=product_id, is_active=True).join(User, Review.user_id == User.id).all()
    user_review = Review.query.filter_by(user_id=current_user.id, product_id=product_id, is_active=True).first() if current_user.is_authenticated else None
    return render_template('product/product_details.html', product=product, cart_item=cart_item, form=form, review_form=review_form, reviews=reviews, user_review=user_review, title=product.name)

@customer_bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    if not current_user.is_authenticated or current_user.role_id != 3:
        flash('Please login as a Customer to add products to the cart...', 'oauth')
        return redirect(url_for('main.home'))
    product = Product.query.filter_by(id=product_id, is_active=True).first_or_404()
    if not product.available or product.quantity <= 0:
        flash('Product Out of Stock...', 'cart')
        return redirect(url_for('customer.product_details', product_id=product_id))
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id, product_status=True).first()
    if cart_item:
        flash('Already Added to Cart...', 'cart')
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1, product_status=True)
        db.session.add(cart_item)
        db.session.commit()
        flash('Product Added to Cart...', 'cart')
    return redirect(url_for('customer.product_details', product_id=product_id))

@customer_bp.route('/cart', methods=['GET'])
@login_required
def view_cart():
    form = AddToCartForm()
    if not current_user.is_authenticated or current_user.role_id != 3:
        flash('Please login as a Customer to add products to the cart...', 'oauth')
        return redirect(url_for('main.home'))
    cart_items = CartItem.query.filter_by(user_id=current_user.id, product_status=True)\
        .join(Product, CartItem.product_id == Product.id)\
        .all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('product/cart.html', cart_items=cart_items, total_price=total_price, form=form, title='Cart')

@customer_bp.route('/cart/update/<int:product_id>', methods=['POST'])
@login_required
def update_cart(product_id):
    form = AddToCartForm()
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id, product_status=True).first_or_404()
    product = Product.query.get_or_404(product_id)
    action = request.form.get('action')
    if action == 'increment' and cart_item.quantity < product.quantity:
        cart_item.quantity += 1
        flash('Quantity Updated...', 'cart')
    elif action == 'decrement' and cart_item.quantity > 1:
        cart_item.quantity -= 1
        flash('Quantity Updated...', 'cart')
    elif action == 'decrement' and cart_item.quantity == 1:
        flash('Cannot Update, use delete instead...', 'cart')
    else:
        flash('Cannot update, product stock limit reached...', 'cart')
    db.session.commit()
    return redirect(url_for('customer.view_cart', form=form,product_id=product_id))

@customer_bp.route('/cart/remove/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id, product_status=True).first_or_404()
    cart_item.product_status = False  
    db.session.commit()
    flash('Product Removed from Cart.', 'cart')
    return redirect(url_for('customer.view_cart', product_id=product_id))

@customer_bp.route('/product/<int:product_id>/review', methods=['POST'])
@login_required
def submit_review(product_id):
    if not current_user.is_authenticated or current_user.role_id != 3:
        flash('Please login as a Customer to submit a review...', 'review')
        return redirect(url_for('customer.product_details', product_id=product_id))
    form = ReviewForm()
    if form.validate_on_submit():
        product = Product.query.get_or_404(product_id)
        existing_review = Review.query.filter_by(user_id=current_user.id, product_id=product_id, is_active=True).first()
        if existing_review:
            flash('You have already reviewed this product...', 'review')
            return redirect(url_for('customer.product_details', product_id=product_id))
        review = Review(
            user_id=current_user.id,
            product_id=product_id,
            rating=form.rating.data,
            comments=form.comment.data,
            is_active=True
        )
        db.session.add(review)
        db.session.commit()
        flash('Review Submitted Successfully...', 'review')
        return redirect(url_for('customer.product_details', product_id=product_id))
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'Error in {field}: {error}', 'review')
    return redirect(url_for('customer.product_details', product_id=product_id))
