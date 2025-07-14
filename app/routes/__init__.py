from .auth import auth_bp
from .main import main_bp
from .admin import admin_bp
from .user_profile import profile_bp
from .product import product_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(product_bp)