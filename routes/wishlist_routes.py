"""
Wishlist Routes
Handles wishlist viewing and management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from models.wishlist import Wishlist
from utils.decorators import login_required

wishlist_bp = Blueprint('wishlist', __name__)


@wishlist_bp.route('/')
@login_required
def view_wishlist():
    """View user's wishlist"""
    user_id = session.get('user_id')
    wishlist_items = Wishlist.get_by_user(user_id)
    return render_template('user/wishlist.html', products=wishlist_items)


@wishlist_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_wishlist(product_id):
    """Add product to wishlist"""
    user_id = session.get('user_id')
    
    if Wishlist.add(user_id, product_id):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'success', 'message': 'Added to wishlist'})
        flash('Product added to wishlist!', 'success')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Could not add to wishlist'})
        flash('Could not add to wishlist.', 'danger')
        
    return redirect(request.referrer or url_for('product.list_products'))


@wishlist_bp.route('/remove/<int:product_id>', methods=['POST'])
@login_required
def remove_from_wishlist(product_id):
    """Remove product from wishlist"""
    user_id = session.get('user_id')
    
    if Wishlist.remove(user_id, product_id):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'success', 'message': 'Removed from wishlist'})
        flash('Product removed from wishlist.', 'info')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Could not remove from wishlist'})
        flash('Could not remove from wishlist.', 'danger')
        
    return redirect(request.referrer or url_for('wishlist.view_wishlist'))
