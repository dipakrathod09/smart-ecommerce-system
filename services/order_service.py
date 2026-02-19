"""
Order Service
Handles business logic for order management, including creation, status updates, 
cancellations, returns, and inventory integration.
"""

import logging
from datetime import datetime
import random
import string
from models.order import Order
from models.cart import Cart
from models.payment import Payment
from services.product_service import ProductService
from database.db_connection import transaction, execute_in_txn, execute_dict_in_txn

logger = logging.getLogger(__name__)

class OrderService:
    """Service for managing orders"""
    
    @staticmethod
    def create_order(user_id, shipping_data):
        """
        Create a new order from cart — ATOMIC TRANSACTION.
        
        The order header, order items, and cart clearing are all executed
        inside a single database transaction. If any step fails, the
        entire operation is rolled back.
        
        Args:
            user_id (int): User ID
            shipping_data (dict): Shipping details
            
        Returns:
            dict: Created order or None
        """
        try:
            # ── 1. READ PHASE (outside transaction) ──────────────────
            cart_items = Cart.get_cart_items(user_id)
            if not cart_items:
                logger.warning(f"Order creation failed: Empty cart for user {user_id}")
                return None
            
            # Validate stock for all items
            for item in cart_items:
                if not ProductService.check_stock(item['product_id'], item['quantity']):
                    logger.warning(f"Order creation failed: Insufficient stock for product {item['product_id']}")
                    return None
            
            cart_total = Cart.get_cart_total(user_id)
            
            # Generate order number
            date_part = datetime.now().strftime('%Y%m%d')
            random_part = ''.join(random.choices(string.digits, k=4))
            order_number = f"ORD{date_part}{random_part}"
            
            # ── 2. WRITE PHASE (atomic transaction) ──────────────────
            with transaction() as conn:
                # 2a. Create order header
                order_query = """
                    INSERT INTO orders (user_id, order_number, total_amount, 
                                      shipping_address, shipping_city, shipping_state,
                                      shipping_pincode, contact_phone, order_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Pending')
                    RETURNING id, order_number, ordered_at
                """
                order = execute_dict_in_txn(
                    conn, order_query,
                    (user_id, order_number, cart_total,
                     shipping_data.get('address'), shipping_data.get('city'),
                     shipping_data.get('state'), shipping_data.get('pincode'),
                     shipping_data.get('phone')),
                    fetch_one=True
                )
                
                if not order:
                    raise RuntimeError("Failed to insert order row")
                
                # 2b. Insert all order items (triggers stock deduction via DB trigger)
                item_query = """
                    INSERT INTO order_items (order_id, product_id, product_name,
                                           product_price, quantity, subtotal)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                for item in cart_items:
                    execute_in_txn(
                        conn, item_query,
                        (order['id'], item['product_id'], item['name'],
                         item['price'], item['quantity'], item['subtotal'])
                    )
                
                # 2c. Clear cart
                execute_in_txn(
                    conn,
                    "DELETE FROM cart WHERE user_id = %s",
                    (user_id,)
                )
            
            # Transaction committed successfully
            logger.info(f"Order created successfully: {order['order_number']} (items: {len(cart_items)}, cart cleared)")
            return order
            
        except Exception as e:
            logger.error(f"Error in create_order service (transaction rolled back): {str(e)}")
            return None

    @staticmethod
    def get_order_by_id(order_id):
        """Get order details"""
        return Order.get_by_id(order_id)

    @staticmethod
    def get_order_details_for_user(order_id, user_id):
        """Get order details with security check"""
        order = Order.get_by_id(order_id)
        if not order or order['user_id'] != user_id:
            return None
        
        # Get items
        order['items'] = Order.get_order_items(order_id)
        # Get payment
        order['payment'] = Payment.get_by_order_id(order_id)
        
        return order

    @staticmethod
    def get_user_orders(user_id, page=1, per_page=10):
        """Get user orders"""
        return Order.get_user_orders(user_id, page, per_page)

    @staticmethod
    def get_all_orders(page=1, per_page=20):
        """Get all orders (Admin)"""
        return Order.get_all_orders(page, per_page)

    @staticmethod
    def update_order_status(order_id, status):
        """Update order status"""
        return Order.update_status(order_id, status)

    @staticmethod
    def cancel_order(order_id, user_id, reason):
        """Cancel an order"""
        order = Order.get_by_id(order_id)
        if not order:
            return False, "Order not found"
            
        if order['user_id'] != user_id:
            return False, "Unauthorized"
            
        if order['order_status'] in ['Delivered', 'Cancelled']:
            return False, "Order cannot be cancelled"
            
        if Order.cancel_order(order_id, reason):
            # Restore stock
            items = Order.get_order_items(order_id)
            for item in items:
                ProductService.update_stock(item['product_id'], item['quantity'])
            
            logger.info(f"Order {order_id} cancelled and stock restored")
            return True, "Order cancelled successfully"
        return False, "Failed to cancel order"

    @staticmethod
    def return_order(order_id, user_id, reason):
        """Return an order"""
        order = Order.get_by_id(order_id)
        if not order:
            return False, "Order not found"
            
        if order['user_id'] != user_id:
            return False, "Unauthorized"
            
        if not order.get('is_returnable'):
            return False, "Order not eligible for return"
            
        if Order.return_order(order_id, reason):
            # Restore stock (assuming returned items are back in inventory)
            items = Order.get_order_items(order_id)
            for item in items:
                ProductService.update_stock(item['product_id'], item['quantity'])
                
            logger.info(f"Order {order_id} returned and stock restored")
            return True, "Return request submitted"
        return False, "Failed to submit return request"

    @staticmethod
    def finalize_order(order_id):
        """
        Finalize order after successful payment.
        Updates status and decrements stock.
        """
        try:
            # 1. Update status
            if not Order.update_status(order_id, 'Confirmed'):
                return False
            
            # Stock is already decremented by DB trigger 'trg_update_stock' on insert
            
            logger.info(f"Order {order_id} finalized")
            return True
        except Exception as e:
            logger.error(f"Error finalizing order {order_id}: {str(e)}")
            return False
