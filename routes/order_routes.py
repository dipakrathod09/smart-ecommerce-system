"""
Order Routes  
Handles order placement, history, and tracking
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services.order_service import OrderService
from models.cart import Cart
from models.user import User
from models.payment import Payment # Keeping for now if needed, but OrderService.get_order_details handles payment fetching
from utils.decorators import login_required
from utils.validators import validate_phone, validate_pincode

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
        # Get and strip shipping details from form
        shipping_address = (request.form.get('address') or '').strip()
        shipping_city = (request.form.get('city') or '').strip()
        shipping_state = (request.form.get('state') or '').strip()
        shipping_pincode = (request.form.get('pincode') or '').strip()
        contact_phone = (request.form.get('phone') or '').strip()
        
        # ── Server-side validation ────────────────────────────────
        errors = []
        
        # Required-field check
        if not shipping_address:
            errors.append('Shipping address is required.')
        elif len(shipping_address) < 5:
            errors.append('Address must be at least 5 characters.')
        elif len(shipping_address) > 500:
            errors.append('Address must be under 500 characters.')
        
        if not shipping_city:
            errors.append('City is required.')
        elif not shipping_city.replace(' ', '').isalpha():
            errors.append('City must contain only letters.')
        elif len(shipping_city) > 50:
            errors.append('City must be under 50 characters.')
        
        if not shipping_state:
            errors.append('State is required.')
        elif not shipping_state.replace(' ', '').isalpha():
            errors.append('State must contain only letters.')
        elif len(shipping_state) > 50:
            errors.append('State must be under 50 characters.')
        
        if not validate_pincode(shipping_pincode):
            errors.append('Pincode must be exactly 6 digits.')
        
        if not validate_phone(contact_phone):
            errors.append('Phone must be exactly 10 digits.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            # Re-render form with existing values preserved
            cart_total = Cart.get_cart_total(user_id)
            user = User.get_by_id(user_id)
            return render_template('user/checkout.html',
                                 cart_items=cart_items,
                                 cart_total=cart_total,
                                 user=user,
                                 form_data={
                                     'address': shipping_address,
                                     'city': shipping_city,
                                     'state': shipping_state,
                                     'pincode': shipping_pincode,
                                     'phone': contact_phone
                                 })
        
        # ── Validation passed — prepare shipping data ─────────────
        shipping_data = {
            'address': shipping_address,
            'city': shipping_city,
            'state': shipping_state,
            'pincode': shipping_pincode,
            'phone': contact_phone
        }

        # Create order via Service
        order = OrderService.create_order(user_id, shipping_data)
        
        if order:
            # Store order ID in session for payment
            session['pending_order_id'] = order['id']
            
            flash('Order created successfully! Please complete payment.', 'success')
            return redirect(url_for('payment.select_method'))
        else:
            flash('Failed to create order. Please check stock or try again.', 'danger')
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
    
    orders = OrderService.get_user_orders(user_id, page=page, per_page=10)
    
    return render_template('user/orders.html', 
                         orders=orders,
                         current_page=page)


@order_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    """View order details"""
    order = OrderService.get_order_details_for_user(order_id, session['user_id'])
    
    if not order:
        flash('Order not found or unauthorized.', 'danger')
        return redirect(url_for('order.order_history'))
    
    return render_template('user/order_detail.html',
                         order=order,
                         order_items=order.get('items', []),
                         payment=order.get('payment'))


@order_bp.route('/cancel/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    """Cancel an order"""
    # Cancel order via Service
    success, message = OrderService.cancel_order(order_id, session['user_id'], 'User Request')
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('order.order_history'))


@order_bp.route('/return/<int:order_id>', methods=['POST'])
@login_required
def return_order(order_id):
    """Return an order"""
    # Return order via Service
    success, message = OrderService.return_order(order_id, session['user_id'], final_reason)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('order.order_history'))
