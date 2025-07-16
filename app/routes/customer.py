from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from ..models import Product, User, Category, CartItem, Review, Discount
from flask_login import login_required, current_user
from .. import db, stripe_publishable_key
from ..forms import AddToCartForm, ReviewForm
import stripe

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
        .join(Product, CartItem.product_id == Product.id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    product_ids = [item.product_id for item in cart_items]
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    product_manager_ids = {product.created_by for product in products}
    discounts = Discount.query.filter(
        Discount.created_by.in_(product_manager_ids),
        Discount.is_active == True
    ).all()
    selected_discount_id = request.args.get('selected_discount', type=int)
    discounted_price = total_price  
    discount_amount = 0
    discount_name = None
    if selected_discount_id:
        selected_discount = Discount.query.get(selected_discount_id)
        if selected_discount and selected_discount.is_active:
            discount_name = selected_discount.name
            if selected_discount.discount_type.name == 'FLAT':
                discount_amount = selected_discount.value
                discounted_price = max(0, total_price - discount_amount)
            elif selected_discount.discount_type.name == 'PERCENT':
                discount_amount = (selected_discount.value / 100) * total_price
                discounted_price = total_price - discount_amount
            flash('Discount Applied Successfully...', 'cart')
    gst_percent = 12
    gst_amount = round(discounted_price * gst_percent / 100, 2)
    final_total = round(discounted_price + gst_amount, 2)
    return render_template(
        'product/cart.html',
        cart_items=cart_items,
        total_price=total_price,
        discounted_price=discounted_price,
        discount_amount=discount_amount,
        discount_name=discount_name,
        gst_amount=gst_amount,
        final_total=final_total,
        discounts=discounts,
        selected_discount_id=selected_discount_id,
        key=stripe_publishable_key,
        form=form,
        title='Cart'
    )


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

@customer_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    if not current_user.is_authenticated or current_user.role_id != 3:
        flash('Please login as a Customer to checkout...', 'oauth')
        return redirect(url_for('main.home'))
    cart_items = CartItem.query.filter_by(user_id=current_user.id, product_status=True)\
        .join(Product, CartItem.product_id == Product.id)\
        .all()
    if not cart_items:
        flash('Your cart is empty...', 'cart')
        return redirect(url_for('customer.view_cart'))
    for item in cart_items:
        if item.quantity > item.product.quantity:
            flash(f'Not enough stock for {item.product.name}. Available: {item.product.quantity}', 'cart')
            return redirect(url_for('customer.view_cart'))
    original_total = sum(item.product.price * item.quantity for item in cart_items)
    selected_discount_id = request.form.get('selected_discount', type=int)
    discount_value = 0
    discount_description = None
    discounted_total = original_total
    coupon_id = None
    if selected_discount_id:
        discount = Discount.query.get(selected_discount_id)
        if discount and discount.is_active:
            discount_description = discount.name
            if discount.discount_type.name == 'FLAT':
                discount_value = discount.value
                discounted_total = max(0, original_total - discount_value)
                coupon = stripe.Coupon.create(
                    name=f"{discount.name} ($ {discount.value} OFF)",
                    amount_off=int(discount_value * 100),
                    currency='usd',
                    duration='once'
                )
                coupon_id = coupon.id
            elif discount.discount_type.name == 'PERCENT':
                discount_value = original_total * (discount.value / 100)
                discounted_total = original_total - discount_value
                coupon = stripe.Coupon.create(
                    name=f"{discount.name} ({discount.value} % OFF)",
                    percent_off=discount.value,
                    duration='once'
                )
                coupon_id = coupon.id
    gst_percent = 12
    cart_base = round(discounted_total, 2)
    gst_amount = round(cart_base * gst_percent / 100, 2)
    final_amount = round(cart_base + gst_amount, 2)
    try:
        line_items = [
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Cart Total (After Discount)',
                    },
                    'unit_amount': int(cart_base * 100),
                },
                'quantity': 1,
            },
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'GST ({gst_percent} %)',
                    },
                    'unit_amount': int(gst_amount * 100),
                },
                'quantity': 1,
            }
        ]
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('customer.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('customer.view_cart', _external=True),
            discounts=[{'coupon': coupon_id}] if coupon_id else [],
            metadata={
                'user_id': str(current_user.id),
                'original_total': str(original_total),
                'discounted_total': str(discounted_total),
                'gst_amount': str(gst_amount),
                'final_amount': str(final_amount),
                'discount_applied': discount_description or 'None'
            }
        )
        return redirect(session.url, code=303)
    except stripe.error.StripeError as e:
        flash(f'Payment error: {str(e)}', 'cart')
        return redirect(url_for('customer.view_cart'))

@customer_bp.route('/success')
@login_required
def success():
    session_id = request.args.get('session_id')
    if not session_id:
        flash('Invalid session...', 'cart')
        return redirect(url_for('customer.view_cart'))
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid' and session.metadata['user_id'] == str(current_user.id):
            cart_items = CartItem.query.filter_by(user_id=current_user.id, product_status=True).all()
            for item in cart_items:
                product = Product.query.get(item.product_id)
                if product.quantity >= item.quantity:
                    product.quantity -= item.quantity
                else:
                    db.session.rollback()
                    flash(f'Payment failed: Not enough stock for {product.name}.', 'cart')
                    return redirect(url_for('customer.view_cart'))
                item.product_status = False
            db.session.commit()
            flash('Payment successful! Your order is confirmed...', 'cart')
        else:
            flash('Payment not completed...', 'cart')
    except stripe.error.StripeError as e:
        flash(f'Error verifying payment: {str(e)}', 'cart')
    return redirect(url_for('customer.view_cart'))