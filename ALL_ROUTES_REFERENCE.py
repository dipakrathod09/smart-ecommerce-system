"""
ALL ROUTES IN ONE FILE
This file contains all route handlers for easy reference.
In actual implementation, each route module should be in its separate file.

ROUTES INCLUDED:
1. Authentication Routes (auth.py)
2. User Routes (user_routes.py)
3. Product Routes (product_routes.py)
4. Cart Routes (cart_routes.py)
5. Order Routes (order_routes.py)
6. Payment Routes (payment_routes.py)
7. Admin Routes (admin_routes.py)
8. Analytics Routes (analytics_routes.py)
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.user import User
from models.admin import Admin
from models.product import Product
from models.category import Category
from models.cart import Cart
from models.order import Order
from models.payment import Payment
from models.recommendation import Recommendation
from models.analytics import Analytics
from functools import wraps

# ===================================================================
# DECORATORS
# File: utils/decorators.py
# ===================================================================

def login_required(f):
    """Decorator to require login for user routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session or not session.get('is_admin'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# ===================================================================
# AUTHENTICATION ROUTES
# File: routes/auth.py
# ===================================================================

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        phone = request.form.get('phone')
        
        # Validation
        if not all([full_name, email, password, confirm_password]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Register user
        user = User.register(full_name, email, password, phone)
        
        if user:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Email already exists. Please use a different email.', 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not all([email, password]):
            flash('Please enter both email and password.', 'danger')
            return redirect(url_for('auth.login'))
        
        user = User.login(email, password)
        
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['user_email'] = user['email']
            session['is_admin'] = False
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')


@auth_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not all([username, password]):
            flash('Please enter both username and password.', 'danger')
            return redirect(url_for('auth.admin_login'))
        
        admin = Admin.login(username, password)
        
        if admin:
            session['admin_id'] = admin['id']
            session['admin_name'] = admin['full_name'] or admin['username']
            session['is_admin'] = True
            session['is_super_admin'] = admin['is_super_admin']
            flash(f'Welcome, {admin["username"]}!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.admin_login'))
    
    return render_template('auth/admin_login.html')


@auth_bp.route('/logout')
def logout():
    """Logout (both user and admin)"""
    is_admin = session.get('is_admin', False)
    session.clear()
    flash('You have been logged out successfully.', 'info')
    
    if is_admin:
        return redirect(url_for('auth.admin_login'))
    return redirect(url_for('index'))


# ===================================================================
# USER ROUTES
# File: routes/user_routes.py
# ===================================================================

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with recommendations"""
    user_id = session['user_id']
    
    # Get recommendations
    recommendations = Recommendation.get_hybrid_recommendations(user_id, limit=8)
    
    # Get recent orders
    recent_orders = Order.get_user_orders(user_id, page=1, per_page=5)
    
    return render_template('user/dashboard.html',
                         recommendations=recommendations,
                         recent_orders=recent_orders)


@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and edit user profile"""
    user_id = session['user_id']
    
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        pincode = request.form.get('pincode')
        
        if User.update_profile(user_id, full_name, phone, address, city, state, pincode):
            session['user_name'] = full_name
            flash('Profile updated successfully!', 'success')
        else:
            flash('Failed to update profile.', 'danger')
        
        return redirect(url_for('user.profile'))
    
    user = User.get_by_id(user_id)
    return render_template('user/profile.html', user=user)


# ===================================================================
# PRODUCT ROUTES
# File: routes/product_routes.py
# ===================================================================

product_bp = Blueprint('product', __name__)

@product_bp.route('/')
def list_products():
    """Product listing with filters and search"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    search_term = request.args.get('search', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort_by', 'created_at')
    
    products = Product.get_all(
        page=page,
        per_page=12,
        category_id=category_id,
        search_term=search_term,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by
    )
    
    total_products = Product.get_total_count(category_id, search_term)
    total_pages = (total_products + 11) // 12
    
    categories = Category.get_all_active_categories()
    
    return render_template('user/products.html',
                         products=products,
                         categories=categories,
                         current_page=page,
                         total_pages=total_pages,
                         selected_category=category_id,
                         search_term=search_term)


@product_bp.route('/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    product = Product.get_by_id(product_id)
    
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('product.list_products'))
    
    # Get related products
    related_products = Recommendation.get_category_based_recommendations(
        product['category_id'],
        limit=4,
        exclude_product_id=product_id
    )
    
    return render_template('user/product_detail.html',
                         product=product,
                         related_products=related_products)


# ===================================================================
# CART ROUTES
# File: routes/cart_routes.py
# ===================================================================

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/')
@login_required
def view_cart():
    """View shopping cart"""
    user_id = session['user_id']
    cart_items = Cart.get_cart_items(user_id)
    cart_total = Cart.get_cart_total(user_id)
    
    return render_template('user/cart.html',
                         cart_items=cart_items,
                         cart_total=cart_total)


@cart_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """Add product to cart"""
    user_id = session['user_id']
    quantity = request.form.get('quantity', 1, type=int)
    
    # Check stock
    if not Product.check_stock(product_id, quantity):
        flash('Insufficient stock.', 'danger')
        return redirect(url_for('product.product_detail', product_id=product_id))
    
    if Cart.add_item(user_id, product_id, quantity):
        flash('Product added to cart!', 'success')
    else:
        flash('Failed to add product to cart.', 'danger')
    
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/update/<int:cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    """Update cart item quantity"""
    quantity = request.form.get('quantity', 1, type=int)
    
    if quantity < 1:
        flash('Invalid quantity.', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    if Cart.update_quantity(cart_id, quantity):
        flash('Cart updated!', 'success')
    else:
        flash('Failed to update cart.', 'danger')
    
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/remove/<int:cart_id>')
@login_required
def remove_from_cart(cart_id):
    """Remove item from cart"""
    if Cart.remove_item(cart_id):
        flash('Item removed from cart.', 'info')
    else:
        flash('Failed to remove item.', 'danger')
    
    return redirect(url_for('cart.view_cart'))


# ===================================================================
# ORDER ROUTES
# File: routes/order_routes.py
# ===================================================================

order_bp = Blueprint('order', __name__)

@order_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page"""
    user_id = session['user_id']
    cart_items = Cart.get_cart_items(user_id)
    
    if not cart_items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('product.list_products'))
    
    if request.method == 'POST':
        # Get shipping details
        shipping_address = request.form.get('address')
        shipping_city = request.form.get('city')
        shipping_state = request.form.get('state')
        shipping_pincode = request.form.get('pincode')
        contact_phone = request.form.get('phone')
        
        # Calculate total
        cart_total = Cart.get_cart_total(user_id)
        
        # Create order
        order = Order.create_order(
            user_id, cart_total, shipping_address,
            shipping_city, shipping_state, shipping_pincode, contact_phone
        )
        
        if order:
            # Add order items
            Order.add_order_items(order['id'], cart_items)
            
            # Store order ID in session for payment
            session['pending_order_id'] = order['id']
            
            return redirect(url_for('payment.select_method'))
        else:
            flash('Failed to create order.', 'danger')
    
    user = User.get_by_id(user_id)
    cart_total = Cart.get_cart_total(user_id)
    
    return render_template('user/checkout.html',
                         cart_items=cart_items,
                         cart_total=cart_total,
                         user=user)


@order_bp.route('/history')
@login_required
def order_history():
    """View order history"""
    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)
    
    orders = Order.get_user_orders(user_id, page=page, per_page=10)
    
    return render_template('user/order_history.html', orders=orders)


@order_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    """View order details"""
    order = Order.get_by_id(order_id)
    
    # Security check
    if not order or order['user_id'] != session['user_id']:
        flash('Order not found.', 'danger')
        return redirect(url_for('order.order_history'))
    
    order_items = Order.get_order_items(order_id)
    payment = Payment.get_by_order_id(order_id)
    
    return render_template('user/order_detail.html',
                         order=order,
                         order_items=order_items,
                         payment=payment)


# ===================================================================
# PAYMENT ROUTES
# File: routes/payment_routes.py
# ===================================================================

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/select-method', methods=['GET', 'POST'])
@login_required
def select_method():
    """Select payment method"""
    order_id = session.get('pending_order_id')
    
    if not order_id:
        flash('No pending order found.', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        
        if payment_method not in ['COD', 'Card', 'UPI']:
            flash('Invalid payment method.', 'danger')
            return redirect(url_for('payment.select_method'))
        
        # Store payment method in session
        session['payment_method'] = payment_method
        
        if payment_method == 'COD':
            return redirect(url_for('payment.process_payment'))
        elif payment_method == 'Card':
            return redirect(url_for('payment.card_details'))
        elif payment_method == 'UPI':
            return redirect(url_for('payment.upi_details'))
    
    order = Order.get_by_id(order_id)
    return render_template('payment/select_method.html', order=order)


@payment_bp.route('/process')
@login_required
def process_payment():
    """Process payment (simulated)"""
    order_id = session.get('pending_order_id')
    payment_method = session.get('payment_method', 'COD')
    
    if not order_id:
        flash('No pending order found.', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    order = Order.get_by_id(order_id)
    
    # Process payment
    payment = Payment.process_payment(order_id, payment_method, order['total_amount'])
    
    if payment and payment['payment_status'] == 'Success':
        # Clear cart
        Cart.clear_cart(session['user_id'])
        
        # Clear session
        session.pop('pending_order_id', None)
        session.pop('payment_method', None)
        
        return render_template('payment/success.html',
                             order=order,
                             payment=payment)
    else:
        return render_template('payment/failed.html',
                             order=order,
                             payment=payment)


# ===================================================================
# ADMIN ROUTES
# File: routes/admin_routes.py
# ===================================================================

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard"""
    stats = Analytics.get_dashboard_stats()
    low_stock = Analytics.get_low_stock_products(threshold=10)
    recent_orders = Order.get_all_orders(page=1, per_page=5)
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         low_stock=low_stock,
                         recent_orders=recent_orders)


@admin_bp.route('/categories')
@admin_required
def manage_categories():
    """Manage categories"""
    categories = Category.get_all_categories()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/products')
@admin_required
def manage_products():
    """Manage products"""
    page = request.args.get('page', 1, type=int)
    products = Product.get_all(page=page, per_page=20)
    total_products = Product.get_total_count()
    total_pages = (total_products + 19) // 20
    
    return render_template('admin/products.html',
                         products=products,
                         current_page=page,
                         total_pages=total_pages)


@admin_bp.route('/orders')
@admin_required
def manage_orders():
    """Manage orders"""
    page = request.args.get('page', 1, type=int)
    orders = Order.get_all_orders(page=page, per_page=20)
    
    return render_template('admin/orders.html', orders=orders)


@admin_bp.route('/order/update-status/<int:order_id>', methods=['POST'])
@admin_required
def update_order_status(order_id):
    """Update order status"""
    new_status = request.form.get('status')
    
    if Order.update_status(order_id, new_status):
        flash('Order status updated!', 'success')
    else:
        flash('Failed to update status.', 'danger')
    
    return redirect(url_for('admin.manage_orders'))


# ===================================================================
# ANALYTICS ROUTES
# File: routes/analytics_routes.py
# ===================================================================

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard')
@admin_required
def dashboard():
    """Analytics dashboard"""
    stats = Analytics.get_dashboard_stats()
    daily_sales = Analytics.get_daily_sales(days=30)
    best_products = Analytics.get_best_selling_products(limit=10)
    category_sales = Analytics.get_category_wise_sales()
    payment_stats = Analytics.get_payment_method_stats()
    
    return render_template('admin/analytics.html',
                         stats=stats,
                         daily_sales=daily_sales,
                         best_products=best_products,
                         category_sales=category_sales,
                         payment_stats=payment_stats)


@analytics_bp.route('/sales-data')
@admin_required
def sales_data():
    """Get sales data for charts (JSON)"""
    daily_sales = Analytics.get_daily_sales(days=30)
    
    # Format for Chart.js
    data = {
        'labels': [str(item['sale_date']) for item in daily_sales],
        'values': [float(item['revenue']) for item in daily_sales]
    }
    
    return jsonify(data)
