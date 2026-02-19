from database.db_connection import execute_query, execute_dict_query
import logging
from datetime import datetime, timedelta
import random
import string

logger = logging.getLogger(__name__)

class Payment:
    """Payment processing model (simulated)"""
    
    @staticmethod
    def generate_transaction_id():
        """Generate unique transaction ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_part = ''.join(random.choices(string.digits, k=6))
        return f"TXN{timestamp}{random_part}"
    
    @staticmethod
    def process_payment(order_id, payment_method, amount, card_last_four=None, upi_id=None):
        """Process payment (simulated)"""
        try:
            transaction_id = Payment.generate_transaction_id()
            
            # For COD, status is initially Pending. For others, it's Success (simulated).
            payment_status = 'Pending' if payment_method == 'COD' else 'Success'
            
            query = """
                INSERT INTO payments (order_id, transaction_id, payment_method, 
                                    amount, payment_status, card_last_four, upi_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (order_id) DO UPDATE SET
                    transaction_id = EXCLUDED.transaction_id,
                    payment_method = EXCLUDED.payment_method,
                    amount = EXCLUDED.amount,
                    payment_status = EXCLUDED.payment_status,
                    card_last_four = EXCLUDED.card_last_four,
                    upi_id = EXCLUDED.upi_id,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id, transaction_id, payment_status
            """
            
            result = execute_dict_query(
                query,
                (order_id, transaction_id, payment_method, amount, 
                 payment_status, card_last_four, upi_id),
                fetch_one=True
            )
            
            if result:
                logger.info(f"Payment record created/updated: {transaction_id} (Status: {payment_status})")
            
            return result
        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}")
            return None

    @staticmethod
    def update_status(order_id, new_status):
        """Update payment status"""
        try:
            query = "UPDATE payments SET payment_status = %s, updated_at = CURRENT_TIMESTAMP WHERE order_id = %s"
            result = execute_query(query, (new_status, order_id), commit=True)
            return (result and result > 0)
        except Exception as e:
            logger.error(f"Error updating payment status: {str(e)}")
            return False
    
    @staticmethod
    def get_by_order_id(order_id):
        """Get payment details by order ID"""
        query = "SELECT * FROM payments WHERE order_id = %s"
        return execute_dict_query(query, (order_id,), fetch_one=True)
    
    @staticmethod
    def get_all_payments(page=1, per_page=20):
        """Get all payments (for admin)"""
        offset = (page - 1) * per_page
        
        query = """
            SELECT p.*, o.order_number, u.full_name as customer_name
            FROM payments p
            JOIN orders o ON p.order_id = o.id
            JOIN users u ON o.user_id = u.id
            ORDER BY p.payment_date DESC
            LIMIT %s OFFSET %s
        """
        return execute_dict_query(query, (per_page, offset), fetch_all=True) or []