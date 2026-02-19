"""
Admin Routes
Handles admin panel, product/category/user/order management
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import os
from werkzeug.utils import secure_filename
from models.admin import Admin
from models.category import Category
from services.product_service import ProductService
from services.order_service import OrderService
from models.user import User
from models.analytics import Analytics
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard"""
    # Get dashboard statistics
    stats = Analytics.get_dashboard_stats()
    
    # Get low stock products
    low_stock = Analytics.get_low_stock_products(threshold=10)
    
    # Get recent orders
    recent_orders = OrderService.get_all_orders(page=1, per_page=5)
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         low_stock=low_stock,
                         recent_orders=recent_orders)


@admin_bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def manage_categories():
    """Manage categories"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('name')
            description = request.form.get('description')
            
            if Category.create(name, description):
                flash('Category added successfully!', 'success')
            else:
                flash('Failed to add category.', 'danger')
        
        elif action == 'edit':
            category_id = request.form.get('category_id', type=int)
            name = request.form.get('name')
            description = request.form.get('description')
            is_active = request.form.get('is_active') == 'on'
            
            if Category.update(category_id, name=name, description=description, is_active=is_active):
                flash('Category updated successfully!', 'success')
            else:
                flash('Failed to update category.', 'danger')
        
        return redirect(url_for('admin.manage_categories'))
    
    categories = Category.get_all_categories()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/products', methods=['GET', 'POST'])
@admin_required
def manage_products():
    """Manage products"""
    page = request.args.get('page', 1, type=int)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        # Handle File Upload
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                import time # Import locally to avoid cluttering top level if not needed elsewhere
                filename = f"{int(time.time())}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                image_url = url_for('static', filename=f'images/products/{filename}')

        if action == 'add':
            category_id = request.form.get('category_id', type=int)
            name = request.form.get('name')
            description = request.form.get('description')
            price = request.form.get('price', type=float)
            stock = request.form.get('stock', type=int)
            brand = request.form.get('brand')
            
            # Use uploaded image URL or fallback to placeholder/form input if we kept it
            # But for now we rely on the file upload. 
            # If no file uploaded, image_url is None (db default or null)
            
            if ProductService.create_product(category_id, name, description, price, stock, brand, image_url):
                flash('Product added successfully!', 'success')
            else:
                flash('Failed to add product.', 'danger')
        
        elif action == 'edit':
            product_id = request.form.get('product_id', type=int)
            name = request.form.get('name')
            price = request.form.get('price', type=float)
            stock = request.form.get('stock', type=int)
            is_active = request.form.get('is_active') == 'on'
            
            # Only update image_url if a new file was uploaded
            update_kwargs = {
                'name': name,
                'price': price,
                'stock': stock,
                'is_active': is_active
            }
            if image_url:
                update_kwargs['image_url'] = image_url
            
            if ProductService.update_product(product_id, **update_kwargs):
                flash('Product updated successfully!', 'success')
            else:
                flash('Failed to update product.', 'danger')
        
        return redirect(url_for('admin.manage_products'))
    
    products = ProductService.get_products(page=page, per_page=20)
    categories = Category.get_all_active_categories()
    
    return render_template('admin/products.html',
                         products=products,
                         categories=categories,
                         current_page=page)


@admin_bp.route('/products/add')
@admin_required
def add_product():
    """Add product form"""
    categories = Category.get_all_active_categories()
    return render_template('admin/add_product.html', categories=categories)


@admin_bp.route('/products/edit/<int:product_id>')
@admin_required
def edit_product(product_id):
    """Edit product form"""
    product = ProductService.get_product_by_id(product_id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('admin.manage_products'))
    categories = Category.get_all_active_categories()
    return render_template('admin/edit_product.html', product=product, categories=categories)


@admin_bp.route('/users')
@admin_required
def manage_users():
    """Manage users"""
    page = request.args.get('page', 1, type=int)
    users = User.get_all_users(page=page, per_page=20)
    
    return render_template('admin/users.html',
                         users=users,
                         current_page=page)


@admin_bp.route('/orders')
@admin_required
def manage_orders():
    """Manage orders"""
    page = request.args.get('page', 1, type=int)
    orders = OrderService.get_all_orders(page=page, per_page=20)
    
    return render_template('admin/orders.html',
                         orders=orders,
                         current_page=page)


@admin_bp.route('/order/update-status/<int:order_id>', methods=['POST'])
@admin_required
def update_order_status(order_id):
    """Update order status"""
    new_status = request.form.get('status')
    
    # Whitelist validation — only allow known statuses
    allowed = current_app.config.get('ORDER_STATUSES', [])
    if new_status not in allowed:
        flash(f'Invalid status. Allowed: {", ".join(allowed)}', 'danger')
        return redirect(url_for('admin.manage_orders'))
    
    if OrderService.update_order_status(order_id, new_status):
        flash('Order status updated!', 'success')
    else:
        flash('Failed to update status.', 'danger')
    
    return redirect(url_for('admin.manage_orders'))


@admin_bp.route('/user/toggle-status/<int:user_id>', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Activate/deactivate user"""
    user = User.get_by_id(user_id)
    
    if user:
        if user['is_active']:
            User.deactivate(user_id)
            flash('User deactivated.', 'info')
        else:
            User.activate(user_id)
            flash('User activated.', 'success')
    else:
        flash('User not found.', 'danger')
    
    return redirect(url_for('admin.manage_users'))
