"""
Routes Package
Contains all route blueprints for the Smart E-Commerce System
"""

from routes.auth import auth_bp
from routes.user_routes import user_bp
from routes.product_routes import product_bp
from routes.cart_routes import cart_bp
from routes.order_routes import order_bp
from routes.payment_routes import payment_bp
from routes.admin_routes import admin_bp
from routes.analytics_routes import analytics_bp

__all__ = [
    'auth_bp',
    'user_bp',
    'product_bp',
    'cart_bp',
    'order_bp',
    'payment_bp',
    'admin_bp',
    'analytics_bp'
]