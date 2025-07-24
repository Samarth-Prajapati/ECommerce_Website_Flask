from flask import Blueprint, jsonify, abort
from ..models import Product, User
from .. import db

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.filter_by(id=id, is_active=True).first_or_404()
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'quantity': product.quantity,
        'available': product.available,
        'category_id': product.category_id,
        'created_by': product.created_by
    })

@api_bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.filter_by(id=id, is_active=True).filter(User.role_id != 1).first_or_404()
    return jsonify({
        'id': user.id,
        'name': f"{user.fname} {user.lname}",
        'gender': user.gender,
        'email': user.email,
        'contact': user.contact or 'N/A',
        'address': user.address or 'N/A',
        'city': user.city or 'N/A',
        'state': user.state or 'N/A',
        'role': 'PRODUCT MANAGER' if user.role_id == 2 else 'CUSTOMER'
    })