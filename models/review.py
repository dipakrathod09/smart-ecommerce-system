"""
Review Model
Handles product reviews and ratings
"""

from database.db_connection import execute_query, execute_dict_query
import logging

logger = logging.getLogger(__name__)


class Review:
    """Review model for managing product ratings"""
    
    @staticmethod
    def create(product_id, user_id, rating, comment=None):
        """
        Create a new review
        
        Args:
            product_id (int): Product ID
            user_id (int): User ID
            rating (int): Rating (1-5)
            comment (str): Optional comment
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check constraints
            if not (1 <= rating <= 5):
                return False
                
            query = """
                INSERT INTO reviews (product_id, user_id, rating, comment)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, product_id) 
                DO UPDATE SET rating = EXCLUDED.rating, comment = EXCLUDED.comment, created_at = CURRENT_TIMESTAMP
            """
            execute_query(query, (product_id, user_id, rating, comment), commit=True)
            return True
        except Exception as e:
            logger.error(f"Error creating review: {str(e)}")
            return False
            
    @staticmethod
    def get_by_product(product_id):
        """
        Get all reviews for a product
        
        Args:
            product_id (int): Product ID
            
        Returns:
            list: List of reviews with user details
        """
        query = """
            SELECT r.*, u.full_name as user_name
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            WHERE r.product_id = %s
            ORDER BY r.created_at DESC
        """
        return execute_dict_query(query, (product_id,), fetch_all=True) or []
        
    @staticmethod
    def get_average_rating(product_id):
        """
        Get average rating and count for a product
        
        Args:
            product_id (int): Product ID
            
        Returns:
            dict: {'average': float, 'count': int}
        """
        query = """
            SELECT AVG(rating) as average, COUNT(*) as count
            FROM reviews
            WHERE product_id = %s
        """
        result = execute_dict_query(query, (product_id,), fetch_one=True)
        if result:
            return {
                'average': float(result['average']) if result['average'] else 0.0,
                'count': result['count']
            }
        return {'average': 0.0, 'count': 0}

    @staticmethod
    def get_user_review(user_id, product_id):
        """
        Get a user's review for a product if it exists
        
        Args:
            user_id (int): User ID
            product_id (int): Product ID
            
        Returns:
            dict: Review data or None
        """
        query = "SELECT * FROM reviews WHERE user_id = %s AND product_id = %s"
        return execute_dict_query(query, (user_id, product_id), fetch_one=True)
