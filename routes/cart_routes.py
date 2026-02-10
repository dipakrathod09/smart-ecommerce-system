"""
Cart Routes
Handles shopping cart operations
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.cart import Cart
from models.product import Product
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
    
    # Validate quantity
    if quantity < 1:
        flash('Invalid quantity.', 'danger')
        return redirect(url_for('product.product_detail', product_id=product_id))
    
    # Check if product exists and has sufficient stock
    if not Product.check_stock(product_id, quantity):
        flash('Insufficient stock or product not available.', 'danger')
        return redirect(url_for('product.product_detail', product_id=product_id))
    
    # Add to cart
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


@cart_bp.route('/clear')
@login_required
def clear_cart():
    """Clear all items from cart"""
    user_id = session['user_id']
    
    if Cart.clear_cart(user_id):
        flash('Cart cleared.', 'info')
    else:
        flash('Failed to clear cart.', 'danger')
    
    return redirect(url_for('cart.view_cart'))
