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
"""
Product Routes
Handles product listing, search, filtering, and details
"""

from flask import Blueprint, render_template, request
from models.product import Product
from models.category import Category
from models.recommendation import Recommendation

# Create blueprint
product_bp = Blueprint('product', __name__)


@product_bp.route('/')
def list_products():
    """Product listing with filters and search"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    search_term = request.args.get('search', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'DESC')
    
    # Get products with filters
    products = Product.get_all(
        page=page,
        per_page=12,
        category_id=category_id,
        search_term=search_term if search_term else None,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Get total count for pagination
    total_products = Product.get_total_count(
        category_id=category_id,
        search_term=search_term if search_term else None
    )
    total_pages = (total_products + 11) // 12  # Ceiling division
    
    # Get all categories for filter sidebar
    categories = Category.get_all_active_categories()
    
    return render_template('user/products.html',
                         products=products,
                         categories=categories,
                         current_page=page,
                         total_pages=total_pages,
                         selected_category=category_id,
                         search_term=search_term,
                         sort_by=sort_by)


@product_bp.route('/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    product = Product.get_by_id(product_id)
    
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('product.list_products'))
    
    # Get related products from same category
    related_products = Recommendation.get_category_based_recommendations(
        product['category_id'],
        limit=4,
        exclude_product_id=product_id
    )
    
    return render_template('user/product_detail.html',
                         product=product,
                         related_products=related_products)


@product_bp.route('/category/<int:category_id>')
def category_products(category_id):
    """Products filtered by category"""
    return list_products()  # Reuse list_products with category filter
