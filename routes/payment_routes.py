"""
Payment Routes
Handles payment method selection and processing (simulated)
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.payment import Payment
from models.order import Order
from models.cart import Cart
from utils.decorators import login_required

payment_bp = Blueprint('payment', __name__)


@payment_bp.route('/select-method', methods=['GET', 'POST'])
@login_required
def select_method():
    """Select payment method"""
    order_id = session.get('pending_order_id')
    
    if not order_id:
        flash('No pending order found.', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        
        # Validate payment method
        if payment_method not in ['COD', 'Card', 'UPI']:
            flash('Invalid payment method selected.', 'danger')
            return redirect(url_for('payment.select_method'))
        
        # Store payment method in session
        session['payment_method'] = payment_method
        
        # Redirect based on payment method
        if payment_method == 'COD':
            return redirect(url_for('payment.process_payment'))
        elif payment_method == 'Card':
            return render_template('payment/card_payment.html', order_id=order_id)
        elif payment_method == 'UPI':
            return render_template('payment/upi_payment.html', order_id=order_id)
    
    # GET request - show method selection
    order = Order.get_by_id(order_id)
    return render_template('payment/select_method.html', order=order)


@payment_bp.route('/process', methods=['GET', 'POST'])
@login_required
def process_payment():
    """Process payment (simulated)"""
    order_id = session.get('pending_order_id')
    payment_method = session.get('payment_method', 'COD')
    
    if not order_id:
        flash('No pending order found.', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    # Get order details
    order = Order.get_by_id(order_id)
    
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    # Get card/UPI details if applicable
    card_last_four = None
    upi_id = None
    
    if request.method == 'POST':
        if payment_method == 'Card':
            card_number = request.form.get('card_number', '')
            card_last_four = card_number[-4:] if len(card_number) >= 4 else None
        elif payment_method == 'UPI':
            upi_id = request.form.get('upi_id')
    
    # Process payment (simulated)
    payment = Payment.process_payment(
        order_id,
        payment_method,
        order['total_amount'],
        card_last_four=card_last_four,
        upi_id=upi_id
    )
    
    if payment and payment['payment_status'] == 'Success':
        # Clear cart after successful payment
        Cart.clear_cart(session['user_id'])
        
        # Clear pending order from session
        session.pop('pending_order_id', None)
        session.pop('payment_method', None)
        
        flash('Payment successful! Your order has been placed.', 'success')
        return render_template('payment/success.html',
                             order=order,
                             payment=payment)
    else:
        flash('Payment failed. Please try again.', 'danger')
        return render_template('payment/failed.html',
                             order=order,
                             payment=payment)
