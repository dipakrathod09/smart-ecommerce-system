"""
User Routes
Handles user dashboard and profile management
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import User
from models.order import Order
from models.recommendation import Recommendation
from utils.decorators import login_required

# Create blueprint
user_bp = Blueprint('user', __name__)


@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with recommendations"""
    user_id = session['user_id']
    
    # Get personalized recommendations
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
            # Update session name if changed
            session['user_name'] = full_name
            flash('Profile updated successfully!', 'success')
        else:
            flash('Failed to update profile.', 'danger')
        
        return redirect(url_for('user.profile'))
    
    # Get current user data
    user = User.get_by_id(user_id)
    return render_template('user/profile.html', user=user)


@user_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    user_id = session['user_id']
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([current_password, new_password, confirm_password]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('user.change_password'))
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('user.change_password'))
        
        if len(new_password) < 6:
            flash('New password must be at least 6 characters.', 'danger')
            return redirect(url_for('user.change_password'))
        
        # Update password
        if User.update_password(user_id, current_password, new_password):
            flash('Password changed successfully!', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('user.change_password'))
    
    return render_template('user/change_password.html')
