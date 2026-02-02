"""
Recommendation Model
Rule-based recommendation engine
"""

from database.db_connection import execute_query, execute_dict_query
import logging

logger = logging.getLogger(__name__)


class Recommendation:
    """Rule-based recommendation engine"""
    
    @staticmethod
    def get_purchase_history_recommendations(user_id, limit=8):
        """
        Recommend products based on user's purchase history
        Returns products from categories the user has bought from before
        
        Args:
            user_id (int): User ID
            limit (int): Maximum number of recommendations
            
        Returns:
            list: List of recommended products
        """
        query = """
            SELECT DISTINCT p.*, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.category_id IN (
                SELECT DISTINCT prod.category_id
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.id
                JOIN products prod ON oi.product_id = prod.id
                WHERE o.user_id = %s
            )
            AND p.is_active = TRUE
            AND p.stock > 0
            AND p.id NOT IN (
                SELECT product_id FROM order_items oi2
                JOIN orders o2 ON oi2.order_id = o2.id
                WHERE o2.user_id = %s
            )
            ORDER BY RANDOM()
            LIMIT %s
        """
        return execute_dict_query(query, (user_id, user_id, limit), fetch_all=True) or []
    
    
    @staticmethod
    def get_category_based_recommendations(category_id, limit=8, exclude_product_id=None):
        """
        Recommend products from same category
        
        Args:
            category_id (int): Category ID
            limit (int): Maximum number of recommendations
            exclude_product_id (int): Product ID to exclude (optional)
            
        Returns:
            list: List of recommended products
        """
        if exclude_product_id:
            query = """
                SELECT p.*, c.name as category_name
                FROM products p
                JOIN categories c ON p.category_id = c.id
                WHERE p.category_id = %s 
                AND p.id != %s
                AND p.is_active = TRUE
                AND p.stock > 0
                ORDER BY RANDOM()
                LIMIT %s
            """
            return execute_dict_query(query, (category_id, exclude_product_id, limit), fetch_all=True) or []
        else:
            query = """
                SELECT p.*, c.name as category_name
                FROM products p
                JOIN categories c ON p.category_id = c.id
                WHERE p.category_id = %s 
                AND p.is_active = TRUE
                AND p.stock > 0
                ORDER BY RANDOM()
                LIMIT %s
            """
            return execute_dict_query(query, (category_id, limit), fetch_all=True) or []
    
    
    @staticmethod
    def get_popular_products(limit=8):
        """
        Get popular/best-selling products
        Based on order count and quantity sold
        
        Args:
            limit (int): Maximum number of products
            
        Returns:
            list: List of popular products
        """
        query = """
            SELECT p.*, c.name as category_name, 
                   COUNT(oi.id) as times_ordered,
                   SUM(oi.quantity) as total_sold
            FROM products p
            JOIN categories c ON p.category_id = c.id
            LEFT JOIN order_items oi ON p.id = oi.product_id
            WHERE p.is_active = TRUE AND p.stock > 0
            GROUP BY p.id, c.name
            ORDER BY total_sold DESC NULLS LAST
            LIMIT %s
        """
        return execute_dict_query(query, (limit,), fetch_all=True) or []
    
    
    @staticmethod
    def get_hybrid_recommendations(user_id, limit=8):
        """
        Hybrid recommendation combining multiple strategies
        
        Strategy weights:
        - 40% from purchase history
        - 30% from popular products
        - 30% random products
        
        Args:
            user_id (int): User ID
            limit (int): Maximum number of recommendations
            
        Returns:
            list: List of recommended products (unique, no duplicates)
        """
        recommendations = []
        
        # 40% from purchase history
        history_recs = Recommendation.get_purchase_history_recommendations(user_id, limit=int(limit * 0.4))
        recommendations.extend(history_recs)
        
        # 30% from popular products
        popular_recs = Recommendation.get_popular_products(limit=int(limit * 0.3))
        recommendations.extend(popular_recs)
        
        # 30% random products
        random_query = """
            SELECT p.*, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.is_active = TRUE AND p.stock > 0
            ORDER BY RANDOM()
            LIMIT %s
        """
        random_recs = execute_dict_query(random_query, (int(limit * 0.3),), fetch_all=True) or []
        recommendations.extend(random_recs)
        
        # Remove duplicates based on product ID
        seen_ids = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec['id'] not in seen_ids:
                seen_ids.add(rec['id'])
                unique_recommendations.append(rec)
                if len(unique_recommendations) >= limit:
                    break
        
        return unique_recommendations
    
    
    @staticmethod
    def get_trending_products(limit=8, days=30):
        """
        Get trending products (most sold in recent period)
        
        Args:
            limit (int): Maximum number of products
            days (int): Number of days to look back
            
        Returns:
            list: List of trending products
        """
        query = """
            SELECT p.*, c.name as category_name,
                   COUNT(oi.id) as recent_orders,
                   SUM(oi.quantity) as recent_quantity
            FROM products p
            JOIN categories c ON p.category_id = c.id
            JOIN order_items oi ON p.id = oi.product_id
            JOIN orders o ON oi.order_id = o.id
            WHERE p.is_active = TRUE 
            AND p.stock > 0
            AND o.ordered_at >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY p.id, c.name
            ORDER BY recent_quantity DESC
            LIMIT %s
        """
        return execute_dict_query(query, (days, limit), fetch_all=True) or []
