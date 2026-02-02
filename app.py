"""
Smart E-Commerce System - Main Application
Flask application with all routes and configurations
"""

from flask import Flask, render_template, session
from datetime import timedelta

# Import configuration
from config import get_config

# Import database
from database.db_connection import initialize_connection_pool, test_connection, close_all_connections

# Import all blueprints
from routes.auth import auth_bp
from routes.user_routes import user_bp
from routes.product_routes import product_bp
from routes.cart_routes import cart_bp
from routes.order_routes import order_bp
from routes.payment_routes import payment_bp
from routes.admin_routes import admin_bp
from routes.analytics_routes import analytics_bp

# Import models for context
from models.cart import Cart
from models.category import Category
from models.product import Product


def create_app():
    """Application factory function"""
    app = Flask(__name__)
    
    # Load configuration
    config = get_config()
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Initialize database connection pool
    print("Initializing database connection pool...")
    if initialize_connection_pool():
        print("✓ Database connection pool initialized")
        if test_connection():
            print("✓ Database connection test successful")
        else:
            print("✗ Database connection test failed")
    else:
        print("✗ Failed to initialize database connection pool")
    
    # Register blueprints with URL prefixes
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(product_bp, url_prefix='/products')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(order_bp, url_prefix='/orders')
    app.register_blueprint(payment_bp, url_prefix='/payment')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    
    print("\n✓ All blueprints registered successfully")
    
    # Context processors
    @app.context_processor
    def inject_user_info():
        """Inject user information into all templates"""
        user_info = {
            'logged_in': 'user_id' in session or 'admin_id' in session,
            'is_admin': session.get('is_admin', False),
            'user_id': session.get('user_id'),
            'user_name': session.get('user_name') or session.get('admin_name'),
            'user_email': session.get('user_email'),
        }
        return {'user_info': user_info}
    
    @app.context_processor
    def inject_cart_count():
        """Inject cart count into all templates"""
        cart_count = 0
        if 'user_id' in session:
            try:
                cart_count = Cart.get_cart_count(session['user_id'])
            except:
                cart_count = 0
        return {'cart_count': cart_count}
    
    # Template filters
    @app.template_filter('currency')
    def currency_filter(value):
        """Format value as currency"""
        try:
            return f"₹{float(value):,.2f}"
        except:
            return f"₹0.00"
    
    @app.template_filter('datetime_format')
    def datetime_format_filter(value, format='%d %b %Y, %I:%M %p'):
        """Format datetime"""
        try:
            return value.strftime(format)
        except:
            return str(value)
    
    @app.template_filter('truncate_text')
    def truncate_text_filter(text, length=100):
        """Truncate text to specified length"""
        if len(text) <= length:
            return text
        return text[:length] + '...'
    
    # Main routes
    @app.route('/')
    def index():
        """Home page"""
        try:
            categories = Category.get_all_active_categories()
            featured_products = Product.get_all(page=1, per_page=8, sort_by='created_at', sort_order='DESC')
            popular_products = []
            if 'user_id' in session:
                from models.recommendation import Recommendation
                popular_products = Recommendation.get_popular_products(limit=4)
            
            return render_template('index.html',
                                 categories=categories,
                                 featured_products=featured_products,
                                 popular_products=popular_products)
        except Exception as e:
            print(f"Error loading homepage: {str(e)}")
            return render_template('index.html',
                                 categories=[],
                                 featured_products=[],
                                 popular_products=[])
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
    return app


# Create the application
app = create_app()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("SMART E-COMMERCE SYSTEM")
    print("="*60)
    print("\nStarting Flask application...")
    print("\nAccess the application at:")
    print("  • Home: http://127.0.0.1:5000/")
    print("  • User Login: http://127.0.0.1:5000/auth/login")
    print("  • Admin Login: http://127.0.0.1:5000/auth/admin-login")
    print("  • User Register: http://127.0.0.1:5000/auth/register")
    print("\nDefault Admin Credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\n" + "="*60 + "\n")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        close_all_connections()
        print("✓ Database connections closed")
        print("Goodbye!\n")
