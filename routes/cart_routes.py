"""
Cart Routes
Handles shopping cart operations
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.cart import Cart
from services.product_service import ProductService
from utils.decorators import login_required

# Create blueprint
cart_bp = Blueprint('cart', __name__)


@cart_bp.route('/')
@login_required
def view_cart():
    """View shopping cart"""
    user_id = session['user_id']
    
    # Get cart items with product details
    cart_items = Cart.get_cart_items(user_id)
    
    # Get cart total
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
    
    # Check for AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Validate quantity
    if quantity < 1:
        if is_ajax:
            return jsonify({'success': False, 'message': 'Invalid quantity.'}), 400
        flash('Invalid quantity.', 'danger')
        return redirect(url_for('product.product_detail', product_id=product_id))
    
    # Check stock (via Service)
    if not ProductService.check_stock(product_id, quantity):
        if is_ajax:
            return jsonify({'success': False, 'message': 'Insufficient stock.'}), 400
        flash('Insufficient stock.', 'danger')
        return redirect(url_for('product.product_detail', product_id=product_id))
    
    # Add to cart
    if Cart.add_item(user_id, product_id, quantity):
        if is_ajax:
            # Get updated cart count
            cart_count = Cart.get_cart_count(user_id)
            return jsonify({'success': True, 'message': 'Product added to cart!', 'cart_count': cart_count})
        flash('Product added to cart!', 'success')
    else:
        if is_ajax:
            return jsonify({'success': False, 'message': 'Failed to add product to cart.'}), 500
        flash('Failed to add product to cart.', 'danger')
    
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/update/<int:cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    """Update cart item quantity"""
    # Helper to check if AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.accept_json
    
    # Get quantity from form or JSON
    if request.is_json:
        data = request.get_json()
        quantity = data.get('quantity', 1)
    else:
        quantity = request.form.get('quantity', 1, type=int)
    
    if quantity < 1:
        if is_ajax:
            return jsonify({'success': False, 'message': 'Invalid quantity.'}), 400
        flash('Invalid quantity.', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    if Cart.update_quantity(cart_id, quantity):
        if is_ajax:
            # Return updated totals
            user_id = session['user_id']
            cart_total = Cart.get_cart_total(user_id)
            # We also need the specific item's new subtotal. 
            # Ideally Cart.update_quantity should return it or we fetch it.
            # Reteching cart items to get updated subtotal for this item
            cart_items = Cart.get_cart_items(user_id)
            item_subtotal = next((item['subtotal'] for item in cart_items if item['cart_id'] == cart_id), 0)
            cart_count = Cart.get_cart_count(user_id)
            
            return jsonify({
                'success': True, 
                'message': 'Cart updated!', 
                'cart_total': cart_total,
                'item_subtotal': item_subtotal,
                'cart_count': cart_count
            })
        flash('Cart updated!', 'success')
    else:
        if is_ajax:
            return jsonify({'success': False, 'message': 'Failed to update cart.'}), 500
        flash('Failed to update cart.', 'danger')
    
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/remove/<int:cart_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_id):
    """Remove item from cart"""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if Cart.remove_item(cart_id):
        if is_ajax:
            user_id = session['user_id']
            cart_total = Cart.get_cart_total(user_id)
            cart_count = Cart.get_cart_count(user_id)
            return jsonify({
                'success': True, 
                'message': 'Item removed from cart.',
                'cart_total': cart_total,
                'cart_count': cart_count
            })
        flash('Item removed from cart.', 'info')
    else:
        if is_ajax:
            return jsonify({'success': False, 'message': 'Failed to remove item.'}), 500
        flash('Failed to remove item.', 'danger')
    
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/clear', methods=['POST'])
@login_required
def clear_cart():
    """Clear all items from cart"""
    user_id = session['user_id']
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if Cart.clear_cart(user_id):
        if is_ajax:
            return jsonify({'success': True, 'message': 'Cart cleared.', 'cart_total': 0, 'cart_count': 0})
        flash('Cart cleared.', 'info')
    else:
        if is_ajax:
            return jsonify({'success': False, 'message': 'Failed to clear cart.'}), 500
        flash('Failed to clear cart.', 'danger')
    
    return redirect(url_for('cart.view_cart'))
