"""
Analytics Model
Handles analytics queries and reporting
"""

from database.db_connection import execute_query, execute_dict_query
import logging

logger = logging.getLogger(__name__)


class Analytics:
    """Analytics and reporting model"""
    
    @staticmethod
    def get_total_revenue():
        """
        Get total revenue from all confirmed orders
        
        Returns:
            float: Total revenue
        """
        query = """
            SELECT COALESCE(SUM(total_amount), 0) as total_revenue
            FROM orders
            WHERE order_status != 'Cancelled'
        """
        result = execute_query(query, fetch_one=True)
        return float(result[0]) if result else 0.0
    
    
    @staticmethod
    def get_total_orders():
        """
        Get total number of orders (excluding cancelled)
        
        Returns:
            int: Total order count
        """
        query = "SELECT COUNT(*) FROM orders WHERE order_status != 'Cancelled'"
        result = execute_query(query, fetch_one=True)
        return result[0] if result else 0
    
    
    @staticmethod
    def get_daily_sales(days=30):
        """
        Get daily sales for last N days
        
        Args:
            days (int): Number of days to look back
            
        Returns:
            list: List of daily sales dictionaries
        """
        query = """
            SELECT DATE(ordered_at) as sale_date,
                   COUNT(*) as order_count,
                   SUM(total_amount) as revenue
            FROM orders
            WHERE ordered_at >= CURRENT_DATE - INTERVAL '%s days'
            AND order_status != 'Cancelled'
            GROUP BY DATE(ordered_at)
            ORDER BY sale_date ASC
        """
        return execute_dict_query(query, (days,), fetch_all=True) or []
    
    
    @staticmethod
    def get_monthly_sales(months=12):
        """
        Get monthly sales for last N months
        
        Args:
            months (int): Number of months to look back
            
        Returns:
            list: List of monthly sales dictionaries
        """
        query = """
            SELECT DATE_TRUNC('month', ordered_at) as sale_month,
                   COUNT(*) as order_count,
                   SUM(total_amount) as revenue
            FROM orders
            WHERE ordered_at >= CURRENT_DATE - INTERVAL '%s months'
            AND order_status != 'Cancelled'
            GROUP BY DATE_TRUNC('month', ordered_at)
            ORDER BY sale_month ASC
        """
        return execute_dict_query(query, (months,), fetch_all=True) or []
    
    
    @staticmethod
    def get_best_selling_products(limit=10):
        """
        Get best-selling products by quantity sold
        
        Args:
            limit (int): Maximum number of products to return
            
        Returns:
            list: List of best-selling products
        """
        query = """
            SELECT p.name, p.price, c.name as category_name,
                   COUNT(oi.id) as times_sold,
                   SUM(oi.quantity) as total_quantity,
                   SUM(oi.subtotal) as total_revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            JOIN categories c ON p.category_id = c.id
            GROUP BY p.id, p.name, p.price, c.name
            ORDER BY total_quantity DESC
            LIMIT %s
        """
        return execute_dict_query(query, (limit,), fetch_all=True) or []
    
    
    @staticmethod
    def get_category_wise_sales():
        """
        Get sales breakdown by category
        
        Returns:
            list: List of category sales dictionaries
        """
        query = """
            SELECT c.name as category_name,
                   COUNT(oi.id) as items_sold,
                   SUM(oi.subtotal) as revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            JOIN categories c ON p.category_id = c.id
            GROUP BY c.id, c.name
            ORDER BY revenue DESC
        """
        return execute_dict_query(query, fetch_all=True) or []
    
    
    @staticmethod
    def get_payment_method_stats():
        """
        Get payment method distribution statistics
        
        Returns:
            list: List of payment method statistics
        """
        query = """
            SELECT payment_method,
                   COUNT(*) as transaction_count,
                   SUM(amount) as total_amount,
                   COUNT(CASE WHEN payment_status = 'Success' THEN 1 END) as successful_count,
                   COUNT(CASE WHEN payment_status = 'Failed' THEN 1 END) as failed_count
            FROM payments
            GROUP BY payment_method
            ORDER BY transaction_count DESC
        """
        return execute_dict_query(query, fetch_all=True) or []
    
    
    @staticmethod
    def get_low_stock_products(threshold=10):
        """
        Get products with stock below threshold
        
        Args:
            threshold (int): Stock threshold
            
        Returns:
            list: List of low stock products
        """
        query = """
            SELECT p.*, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.stock < %s AND p.is_active = TRUE
            ORDER BY p.stock ASC
        """
        return execute_dict_query(query, (threshold,), fetch_all=True) or []
    
    
    @staticmethod
    def get_dashboard_stats():
        """
        Get overall dashboard statistics
        
        Returns:
            dict: Dashboard statistics
        """
        return {
            'total_revenue': Analytics.get_total_revenue(),
            'total_orders': Analytics.get_total_orders(),
            'total_users': Analytics.get_total_users(),
            'total_products': Analytics.get_total_products(),
            'low_stock_count': len(Analytics.get_low_stock_products()),
            'pending_orders': Analytics.get_pending_orders_count()
        }
    
    
    @staticmethod
    def get_total_users():
        """
        Get total number of active users
        
        Returns:
            int: Total user count
        """
        query = "SELECT COUNT(*) FROM users WHERE is_active = TRUE"
        result = execute_query(query, fetch_one=True)
        return result[0] if result else 0
    
    
    @staticmethod
    def get_total_products():
        """
        Get total number of active products
        
        Returns:
            int: Total product count
        """
        query = "SELECT COUNT(*) FROM products WHERE is_active = TRUE"
        result = execute_query(query, fetch_one=True)
        return result[0] if result else 0
    
    
    @staticmethod
    def get_pending_orders_count():
        """
        Get count of pending orders
        
        Returns:
            int: Pending order count
        """
        query = "SELECT COUNT(*) FROM orders WHERE order_status = 'Pending'"
        result = execute_query(query, fetch_one=True)
        return result[0] if result else 0
    
    
    @staticmethod
    def get_revenue_by_date_range(start_date, end_date):
        """
        Get revenue for a specific date range
        
        Args:
            start_date (date): Start date
            end_date (date): End date
            
        Returns:
            float: Total revenue in date range
        """
        query = """
            SELECT COALESCE(SUM(total_amount), 0) as revenue
            FROM orders
            WHERE DATE(ordered_at) BETWEEN %s AND %s
            AND order_status != 'Cancelled'
        """
        result = execute_query(query, (start_date, end_date), fetch_one=True)
        return float(result[0]) if result else 0.0
    
    
    @staticmethod
    def get_top_customers(limit=10):
        """
        Get top customers by total purchase amount
        
        Args:
            limit (int): Number of customers to return
            
        Returns:
            list: List of top customers
        """
        query = """
            SELECT u.id, u.full_name, u.email,
                   COUNT(o.id) as order_count,
                   SUM(o.total_amount) as total_spent
            FROM users u
            JOIN orders o ON u.id = o.user_id
            WHERE o.order_status != 'Cancelled'
            GROUP BY u.id, u.full_name, u.email
            ORDER BY total_spent DESC
            LIMIT %s
        """
        return execute_dict_query(query, (limit,), fetch_all=True) or []
