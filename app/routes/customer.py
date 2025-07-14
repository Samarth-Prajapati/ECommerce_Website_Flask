from flask import Blueprint, render_template
from ..models import Product, User, Category

customer_bp = Blueprint('customer', __name__, url_prefix = '/customer')

@customer_bp.route('/men', methods=['GET', 'POST'])
def men():
    products = Product.query.filter_by(is_active=True)\
    .join(User, Product.created_by == User.id)\
    .join(Category, Product.category_id == Category.id)\
    .filter(Category.name == 'MEN')\
    .all()
    return render_template('product/men.html',products=products ,title='men')
