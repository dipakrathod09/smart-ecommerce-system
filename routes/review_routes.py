"""
Review Routes
Handles adding and viewing product reviews
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from models.review import Review
from utils.decorators import login_required

review_bp = Blueprint('review', __name__)


@review_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    """Add or update a review"""
    user_id = session.get('user_id')
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment')
    
    if not rating or not (1 <= rating <= 5):
        flash('Please provide a valid rating (1-5 stars).', 'danger')
        return redirect(url_for('product.product_detail', product_id=product_id))
        
    if Review.create(product_id, user_id, rating, comment):
        flash('Review submitted successfully!', 'success')
    else:
        flash('Failed to submit review.', 'danger')
        
    return redirect(url_for('product.product_detail', product_id=product_id))
