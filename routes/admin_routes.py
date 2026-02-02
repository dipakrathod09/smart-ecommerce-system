"""
Admin Routes
Handles admin panel, product/category/user/order management
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.admin import Admin
from models.category import Category
from models.product import Product
from models.user import User
from models.order import Order
from models.analytics import Analytics
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard"""
    # Get dashboard statistics
    stats = Analytics.get_dashboard_stats()
    
    # Get low stock products
    low_stock = Analytics.get_low_stock_products(threshold=10)
    
    # Get recent orders
    recent_orders = Order.get_all_orders(page=1, per_page=5)
    
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
        
        if action == 'add':
            category_id = request.form.get('category_id', type=int)
            name = request.form.get('name')
            description = request.form.get('description')
            price = request.form.get('price', type=float)
            stock = request.form.get('stock', type=int)
            brand = request.form.get('brand')
            
            if Product.create(category_id, name, description, price, stock, brand):
                flash('Product added successfully!', 'success')
            else:
                flash('Failed to add product.', 'danger')
        
        elif action == 'edit':
            product_id = request.form.get('product_id', type=int)
            name = request.form.get('name')
            price = request.form.get('price', type=float)
            stock = request.form.get('stock', type=int)
            is_active = request.form.get('is_active') == 'on'
            
            if Product.update(product_id, name=name, price=price, stock=stock, is_active=is_active):
                flash('Product updated successfully!', 'success')
            else:
                flash('Failed to update product.', 'danger')
        
        return redirect(url_for('admin.manage_products'))
    
    products = Product.get_all(page=page, per_page=20)
    categories = Category.get_all_active_categories()
    
    return render_template('admin/products.html',
                         products=products,
                         categories=categories,
                         current_page=page)


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
    orders = Order.get_all_orders(page=page, per_page=20)
    
    return render_template('admin/orders.html',
                         orders=orders,
                         current_page=page)


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


@admin_bp.route('/user/toggle-status/<int:user_id>')
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
