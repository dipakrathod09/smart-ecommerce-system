"""
Product Routes
Handles product listing, search, filtering, and details
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.product import Product
from models.category import Category
from models.recommendation import Recommendation
from models.wishlist import Wishlist
from utils.decorators import login_required

# Create blueprint
product_bp = Blueprint('product', __name__)


@product_bp.route('/')
def list_products():
    """List all products with filtering"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    search_term = request.args.get('search')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'DESC')
    
    products = Product.get_all(
        page=page, 
        per_page=12, 
        category_id=category_id, 
        search_term=search_term,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    total_products = Product.get_total_count(
        category_id=category_id,
        search_term=search_term
    )
    total_pages = (total_products + 11) // 12  # Ceiling division
    
    # Get all categories for filter sidebar
    categories = Category.get_all_active_categories()
    
    # Get user's wishlist if logged in
    wishlist_product_ids = set()
    if 'user_id' in session:
        wishlist_product_ids = Wishlist.get_user_wishlist_ids(session['user_id'])
    
    return render_template('user/products.html',
                         products=products,
                         categories=categories,
                         current_page=page,
                         total_pages=total_pages,
                         selected_category=category_id,
                         search_term=search_term,
                         sort_by=sort_by,
                         wishlist_product_ids=wishlist_product_ids)


@product_bp.route('/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    product = Product.get_by_id(product_id)
    
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('product.list_products'))
    
    # Get related products from same category
    related_products = Product.get_related_products(
        product_id,
        limit=4
    )
    
    # Check if in wishlist
    in_wishlist = False
    if 'user_id' in session:
        in_wishlist = Wishlist.check(session['user_id'], product_id)

    # Get reviews and rating
    from models.review import Review
    reviews = Review.get_by_product(product_id)
    rating_stats = Review.get_average_rating(product_id)
    user_review = None
    if 'user_id' in session:
        user_review = Review.get_user_review(session['user_id'], product_id)
    
    return render_template('user/product_detail.html',
                         product=product,
                         related_products=related_products,
                         in_wishlist=in_wishlist,
                         reviews=reviews,
                         rating_stats=rating_stats,
                         user_review=user_review)


@product_bp.route('/category/<int:category_id>')
def category_products(category_id):
    """Products filtered by category"""
    return list_products()  # Reuse list_products with category filter


@product_bp.route('/search/suggestions')
def search_suggestions():
    """API endpoint for search autocomplete"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
        
    suggestions = Product.get_search_suggestions(query)
    return jsonify(suggestions)
