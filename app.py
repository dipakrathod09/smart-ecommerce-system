"""
Smart E-Commerce System - Main Application Entry Point
This is the main Flask application file that initializes and runs the server
"""

from flask import Flask, render_template, session, redirect, url_for
from flask.json.provider import DefaultJSONProvider
from flask_wtf.csrf import CSRFProtect
from config import get_config
from decimal import Decimal
from datetime import date, datetime
import os


# ── Custom JSON provider for PostgreSQL types ────────────────────
class CustomJSONProvider(DefaultJSONProvider):
    """Handle Decimal and date types returned by PostgreSQL queries."""
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        return super().default(o)


# Initialize Flask app
app = Flask(__name__)
app.json_provider_class = CustomJSONProvider
app.json = CustomJSONProvider(app)

# Load configuration
app.config.from_object(get_config())

# Enable CSRF protection globally
csrf = CSRFProtect(app)

# Initialize Rate Limiter
from extensions import limiter
limiter.init_app(app)


# ===================================================================
# SECURITY HEADERS
# ===================================================================

@app.after_request
def add_security_headers(response):
    """Add security headers to response"""
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://code.jquery.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
        "img-src 'self' data:; "
        "connect-src 'self';"
    )
    response.headers['Content-Security-Policy'] = csp
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# ===================================================================
# IMPORT AND REGISTER BLUEPRINTS (Routes)
# ===================================================================

from routes.auth import auth_bp
from routes.user_routes import user_bp
from routes.product_routes import product_bp
from routes.cart_routes import cart_bp
from routes.order_routes import order_bp
from routes.payment_routes import payment_bp
from routes.admin_routes import admin_bp
from routes.analytics_routes import analytics_bp
from routes.wishlist_routes import wishlist_bp
from routes.review_routes import review_bp

# Register blueprints with URL prefixes
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(product_bp, url_prefix='/products')
app.register_blueprint(cart_bp, url_prefix='/cart')
app.register_blueprint(order_bp, url_prefix='/orders')
app.register_blueprint(payment_bp, url_prefix='/payment')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(analytics_bp, url_prefix='/analytics')
app.register_blueprint(wishlist_bp, url_prefix='/wishlist')
app.register_blueprint(review_bp, url_prefix='/reviews')

# ===================================================================
# TEMPLATE FILTERS (Custom Jinja2 filters)
# ===================================================================

from utils.helpers import format_currency, format_datetime, truncate_text

@app.template_filter('currency')
def currency_filter(value):
    """Format number as currency (INR)"""
    return format_currency(value)


@app.template_filter('datetime_format')
def datetime_format_filter(value, format='%d %b %Y, %I:%M %p'):
    """Format datetime object"""
    return format_datetime(value, format)


@app.template_filter('truncate_text')
def truncate_text_filter(text, length=100):
    """Truncate text to specified length"""
    return truncate_text(text, length)


# ===================================================================
# CONTEXT PROCESSORS (Make variables available to all templates)
# ===================================================================

@app.context_processor
def inject_cart_count():
    """Inject cart item count into all templates"""
    cart_count = 0
    if 'user_id' in session:
        try:
            from models.cart import Cart
            cart_count = Cart.get_cart_count(session['user_id'])
        except:
            cart_count = 0
    return dict(cart_count=cart_count)


@app.context_processor
def inject_user_info():
    """Inject user information into all templates"""
    user_info = {
        'logged_in': 'user_id' in session,
        'is_admin': session.get('is_admin', False),
        'user_name': session.get('user_name', ''),
        'user_email': session.get('user_email', '')
    }
    return dict(user_info=user_info)


# ===================================================================
# ERROR HANDLERS
# ===================================================================

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors"""
    return render_template('errors/500.html'), 500


@app.errorhandler(403)
def forbidden(e):
    """Handle 403 errors"""
    return render_template('errors/403.html'), 403


# ===================================================================
# MAIN ROUTES
# ===================================================================

@app.route('/')
def index():
    """Home page - shows featured products and categories"""
    try:
        from services.product_service import ProductService
        from models.category import Category
        from models.recommendation import Recommendation
        from models.wishlist import Wishlist
        
        # Get featured products (latest 8 products)
        featured_products = ProductService.get_featured_products(limit=8)
        
        # Get all active categories
        categories = Category.get_all_active_categories()
        
        # Get popular products & wishlist if user is logged in
        popular_products = []
        wishlist_product_ids = set()
        
        if 'user_id' in session:
            popular_products = Recommendation.get_popular_products(limit=4)
            wishlist_product_ids = Wishlist.get_user_wishlist_ids(session['user_id'])
        
        return render_template('index.html',
                             featured_products=featured_products,
                             categories=categories,
                             popular_products=popular_products,
                             wishlist_product_ids=wishlist_product_ids)
    except Exception as e:
        app.logger.error(f"Error loading home page: {str(e)}")
        return render_template('index.html',
                             featured_products=[],
                             categories=[],
                             popular_products=[],
                             wishlist_product_ids=set())


@app.route('/about')
def about():
    """About us page"""
    return render_template('about.html')


@app.route('/contact')
def contact():
    """Contact us page"""
    return render_template('contact.html')


@app.route('/return-policy')
def return_policy():
    """Return policy page"""
    return render_template('return_policy.html')



# ===================================================================
# APPLICATION STARTUP
# ===================================================================


def create_upload_folders():
    """Create upload folders if they don't exist"""
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        app.logger.info(f"Created upload folder: {upload_folder}")


def ensure_admin_exists():
    """Ensure default admin account exists (auto-create on startup)"""
    try:
        from models.admin import Admin
        from database.db_connection import execute_query
        
        # Check if any admin exists
        result = execute_query("SELECT COUNT(*) FROM admin", fetch_one=True)
        
        if result and result[0] == 0:
            # No admin exists, create default admin
            app.logger.info("No admin account found. Creating default admin...")
            
            default_username = os.environ.get('DEFAULT_ADMIN_USERNAME', 'admin')
            default_password = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'admin123')
            default_email = os.environ.get('DEFAULT_ADMIN_EMAIL', 'admin@smartecommerce.com')
            
            admin = Admin.create_admin(
                username=default_username,
                password=default_password,
                email=default_email,
                full_name='System Administrator',
                is_super_admin=True
            )
            
            if admin:
                app.logger.info("✓ Default admin account created successfully")
                app.logger.info(f"  Username: {default_username} (change password immediately!)")
            else:
                app.logger.warning("Failed to create default admin account")
        else:
            app.logger.info("Admin account verified")
            
    except Exception as e:
        app.logger.error(f"Error checking/creating admin account: {str(e)}")


def initialize_app():
    """Initialize application (run before first request)"""
    create_upload_folders()
    ensure_admin_exists()  # Auto-create admin if needed
    app.logger.info("Application initialized successfully")



# ===================================================================
# RUN APPLICATION
# ===================================================================

if __name__ == '__main__':
    # Initialize application
    initialize_app()
    
    # Run Flask development server
    app.run(
        host='0.0.0.0',  # Listen on all network interfaces
        port=5000,        # Port number
        debug=app.config['DEBUG']  # Enable debug mode from config
    )
    
    # For production, use a WSGI server like Gunicorn:
    # gunicorn -w 4 -b 0.0.0.0:5000 app:app
