"""
Wishlist Model
Handles wishlist operations
"""

from database.db_connection import execute_query, execute_dict_query
import logging

logger = logging.getLogger(__name__)


class Wishlist:
    """Wishlist model for managing user favorites"""
    
    @staticmethod
    def add(user_id, product_id):
        """
        Add product to wishlist
        
        Args:
            user_id (int): User ID
            product_id (int): Product ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            query = """
                INSERT INTO wishlists (user_id, product_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id, product_id) DO NOTHING
            """
            execute_query(query, (user_id, product_id), commit=True)
            return True
        except Exception as e:
            logger.error(f"Error adding to wishlist: {str(e)}")
            return False
            
    @staticmethod
    def remove(user_id, product_id):
        """
        Remove product from wishlist
        
        Args:
            user_id (int): User ID
            product_id (int): Product ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            query = "DELETE FROM wishlists WHERE user_id = %s AND product_id = %s"
            result = execute_query(query, (user_id, product_id), commit=True)
            return True
        except Exception as e:
            logger.error(f"Error removing from wishlist: {str(e)}")
            return False
            
    @staticmethod
    def get_by_user(user_id):
        """
        Get all wishlist items for a user
        
        Args:
            user_id (int): User ID
            
        Returns:
            list: List of products in wishlist
        """
        query = """
            SELECT p.*, c.name as category_name, w.created_at as added_at
            FROM wishlists w
            JOIN products p ON w.product_id = p.id
            JOIN categories c ON p.category_id = c.id
            WHERE w.user_id = %s
            ORDER BY w.created_at DESC
        """
        return execute_dict_query(query, (user_id,), fetch_all=True) or []
        
    @staticmethod
    def check(user_id, product_id):
        """
        Check if product is in wishlist
        
        Args:
            user_id (int): User ID
            product_id (int): Product ID
            
        Returns:
            bool: True if in wishlist, False otherwise
        """
        query = "SELECT 1 FROM wishlists WHERE user_id = %s AND product_id = %s"
        result = execute_query(query, (user_id, product_id), fetch_one=True)
        return bool(result)
    
    @staticmethod
    def get_user_wishlist_ids(user_id):
        """
        Get set of product IDs in user's wishlist (for quick lookup)
        
        Args:
            user_id (int): User ID
            
        Returns:
            set: Set of product IDs
        """
        query = "SELECT product_id FROM wishlists WHERE user_id = %s"
        results = execute_dict_query(query, (user_id,), fetch_all=True)
        if results:
            return {row['product_id'] for row in results}
        return set()

    @staticmethod
    def delete_by_product(product_id):
        """
        Remove product from all wishlists
        
        Args:
            product_id (int): Product ID
            
        Returns:
            bool: True if successful
        """
        try:
            query = "DELETE FROM wishlists WHERE product_id = %s"
            execute_query(query, (product_id,), commit=True)
            return True
        except Exception as e:
            logger.error(f"Error removing product {product_id} from wishlists: {str(e)}")
            return False
