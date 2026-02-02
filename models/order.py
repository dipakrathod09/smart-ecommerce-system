"""
Order Model
Handles order creation and management
"""

from database.db_connection import execute_query, execute_dict_query
import logging
from datetime import datetime
import random
import string

logger = logging.getLogger(__name__)


class Order:
    """Order management model"""
    
    @staticmethod
    def generate_order_number():
        """
        Generate unique order number
        Format: ORD20260201XXXX
        
        Returns:
            str: Unique order number
        """
        date_part = datetime.now().strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"ORD{date_part}{random_part}"
    
    
    @staticmethod
    def create_order(user_id, total_amount, shipping_address, shipping_city,
                    shipping_state, shipping_pincode, contact_phone):
        """
        Create a new order
        
        Args:
            user_id (int): User ID
            total_amount (float): Total order amount
            shipping_address (str): Shipping address
            shipping_city (str): Shipping city
            shipping_state (str): Shipping state
            shipping_pincode (str): Shipping PIN code
            contact_phone (str): Contact phone number
            
        Returns:
            dict: Created order data or None
        """
        try:
            order_number = Order.generate_order_number()
            
            query = """
                INSERT INTO orders (user_id, order_number, total_amount, 
                                  shipping_address, shipping_city, shipping_state,
                                  shipping_pincode, contact_phone, order_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Pending')
                RETURNING id, order_number, ordered_at
            """
            
            result = execute_dict_query(
                query,
                (user_id, order_number, total_amount, shipping_address,
                 shipping_city, shipping_state, shipping_pincode, contact_phone),
                fetch_one=True
            )
            
            if result:
                logger.info(f"Order created: {order_number}")
                return result
            return None
            
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            return None
    
    
    @staticmethod
    def add_order_items(order_id, cart_items):
        """
        Add items to order from cart
        
        Args:
            order_id (int): Order ID
            cart_items (list): List of cart item dictionaries
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            for item in cart_items:
                query = """
                    INSERT INTO order_items (order_id, product_id, product_name,
                                           product_price, quantity, subtotal)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                execute_query(
                    query,
                    (order_id, item['product_id'], item['name'],
                     item['price'], item['quantity'], item['subtotal']),
                    commit=True
                )
            logger.info(f"Added {len(cart_items)} items to order {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding order items: {str(e)}")
            return False
    
    
    @staticmethod
    def get_by_id(order_id):
        """
        Get order by ID with user details
        
        Args:
            order_id (int): Order ID
            
        Returns:
            dict: Order data with user details or None
        """
        query = """
            SELECT o.*, u.full_name as customer_name, u.email as customer_email
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.id = %s
        """
        return execute_dict_query(query, (order_id,), fetch_one=True)
    
    
    @staticmethod
    def get_order_items(order_id):
        """
        Get items for an order
        
        Args:
            order_id (int): Order ID
            
        Returns:
            list: List of order item dictionaries
        """
        query = """
            SELECT * FROM order_items
            WHERE order_id = %s
            ORDER BY id
        """
        return execute_dict_query(query, (order_id,), fetch_all=True) or []
    
    
    @staticmethod
    def get_user_orders(user_id, page=1, per_page=10):
        """
        Get orders for a user with pagination
        
        Args:
            user_id (int): User ID
            page (int): Page number
            per_page (int): Items per page
            
        Returns:
            list: List of order dictionaries
        """
        offset = (page - 1) * per_page
        
        query = """
            SELECT o.*, p.payment_status, p.payment_method
            FROM orders o
            LEFT JOIN payments p ON o.id = p.order_id
            WHERE o.user_id = %s
            ORDER BY o.ordered_at DESC
            LIMIT %s OFFSET %s
        """
        return execute_dict_query(query, (user_id, per_page, offset), fetch_all=True) or []
    
    
    @staticmethod
    def get_all_orders(page=1, per_page=20):
        """
        Get all orders (for admin)
        
        Args:
            page (int): Page number
            per_page (int): Items per page
            
        Returns:
            list: List of all order dictionaries
        """
        offset = (page - 1) * per_page
        
        query = """
            SELECT o.*, u.full_name as customer_name, u.email as customer_email,
                   p.payment_status, p.payment_method
            FROM orders o
            JOIN users u ON o.user_id = u.id
            LEFT JOIN payments p ON o.id = p.order_id
            ORDER BY o.ordered_at DESC
            LIMIT %s OFFSET %s
        """
        return execute_dict_query(query, (per_page, offset), fetch_all=True) or []
    
    
    @staticmethod
    def update_status(order_id, new_status):
        """
        Update order status
        
        Args:
            order_id (int): Order ID
            new_status (str): New status
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = "UPDATE orders SET order_status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
        result = execute_query(query, (new_status, order_id), commit=True)
        
        if result and result > 0:
            logger.info(f"Order {order_id} status updated to {new_status}")
            return True
        return False
    
    
    @staticmethod
    def get_order_count():
        """
        Get total order count
        
        Returns:
            int: Total number of orders
        """
        query = "SELECT COUNT(*) FROM orders"
        result = execute_query(query, fetch_one=True)
        return result[0] if result else 0
