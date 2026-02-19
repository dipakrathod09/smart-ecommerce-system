"""
Order Routes  
Handles order placement, history, and tracking
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.order import Order
from models.cart import Cart
from models.user import User
from models.payment import Payment
from utils.decorators import login_required

order_bp = Blueprint('order', __name__)


@order_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page"""
    user_id = session['user_id']
    
    # Get cart items
    cart_items = Cart.get_cart_items(user_id)
    
    if not cart_items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('product.list_products'))
    
    if request.method == 'POST':
        # Get shipping details from form
        shipping_address = request.form.get('address')
        shipping_city = request.form.get('city')
        shipping_state = request.form.get('state')
        shipping_pincode = request.form.get('pincode')
        contact_phone = request.form.get('phone')
        
        # Validate required fields
        if not all([shipping_address, shipping_city, shipping_state, shipping_pincode, contact_phone]):
            flash('All shipping details are required.', 'danger')
            return redirect(url_for('order.checkout'))
        
        # Calculate total
        cart_total = Cart.get_cart_total(user_id)
        
        # Create order
        order = Order.create_order(
            user_id, cart_total, shipping_address,
            shipping_city, shipping_state, shipping_pincode, contact_phone
        )
        
        if order:
            # Add order items from cart
            Order.add_order_items(order['id'], cart_items)
            
            # Store order ID in session for payment
            session['pending_order_id'] = order['id']
            
            flash('Order created successfully! Please complete payment.', 'success')
            return redirect(url_for('payment.select_method'))
        else:
            flash('Failed to create order. Please try again.', 'danger')
            return redirect(url_for('order.checkout'))
    
    # GET request - show checkout form
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
    
    return render_template('user/orders.html', 
                         orders=orders,
                         current_page=page)


@order_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    """View order details"""
    order = Order.get_by_id(order_id)
    
    # Security check - ensure order belongs to logged-in user
    if not order or order['user_id'] != session['user_id']:
        flash('Order not found.', 'danger')
        return redirect(url_for('order.order_history'))
    
    # Get order items
    order_items = Order.get_order_items(order_id)
    
    # Get payment details
    payment = Payment.get_by_order_id(order_id)
    
    return render_template('user/order_detail.html',
                         order=order,
                         order_items=order_items,
                         payment=payment)


@order_bp.route('/cancel/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    """Cancel an order"""
    order = Order.get_by_id(order_id)
    
    # Security check - ensure order belongs to logged-in user
    if not order or order['user_id'] != session['user_id']:
        flash('Order not found.', 'danger')
        return redirect(url_for('order.order_history'))
    
    # Check if order can be cancelled
    if order['order_status'] in ['Delivered', 'Cancelled']:
        flash('This order cannot be cancelled.', 'warning')
        return redirect(url_for('order.order_history'))
    
    # Update order status to Cancelled
    if Order.update_status(order_id, 'Cancelled'):
        flash(f'Order #{order["order_number"]} has been cancelled successfully.', 'success')
    else:
        flash('Failed to cancel order. Please try again.', 'danger')
    
    return redirect(url_for('order.order_history'))


@order_bp.route('/return/<int:order_id>', methods=['POST'])
@login_required
def return_order(order_id):
    """Return an order"""
    order = Order.get_by_id(order_id)
    
    # Security check - ensure order belongs to logged-in user
    if not order or order['user_id'] != session['user_id']:
        flash('Order not found.', 'danger')
        return redirect(url_for('order.order_history'))
    
    # Check if order can be returned (must be Delivered and within 7 days)
    if not order.get('is_returnable'):
        flash('This order is not eligible for return (must be within 7 days of delivery).', 'warning')
        return redirect(url_for('order.order_history'))
    
    return_reason = request.form.get('return_reason')
    other_reason = request.form.get('other_reason')

    # Combine selection and detailed text
    if return_reason and other_reason:
        final_reason = f"[{return_reason}] {other_reason}"
    else:
        final_reason = return_reason or other_reason

    if not final_reason:
        flash('Please provide a reason for return.', 'warning')
        return redirect(url_for('order.order_history'))
    
    # Update order status to Returned
    if Order.return_order(order_id, final_reason):
        flash(f'Return request for Order #{order["order_number"]} has been submitted successfully.', 'success')
    else:
        flash('Failed to process return request. Please try again.', 'danger')
    
    return redirect(url_for('order.order_history'))
