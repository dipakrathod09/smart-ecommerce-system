from database.db_connection import execute_query, execute_dict_query
import logging
from datetime import datetime, timedelta
import random
import string

logger = logging.getLogger(__name__)

class Category:
    """Category model for product categorization"""
    
    @staticmethod
    def create(name, description=None, image_url=None):
        """Create a new category"""
        try:
            query = """
                INSERT INTO categories (name, description, image_url)
                VALUES (%s, %s, %s)
                RETURNING id, name, created_at
            """
            result = execute_dict_query(query, (name, description, image_url), fetch_one=True)
            if result:
                logger.info(f"Category created: {name}")
            return result
        except Exception as e:
            logger.error(f"Error creating category: {str(e)}")
            return None
    
    @staticmethod
    def get_all_active_categories():
        """Get all active categories"""
        query = """
            SELECT id, name, description, image_url
            FROM categories
            WHERE is_active = TRUE
            ORDER BY name ASC
        """
        return execute_dict_query(query, fetch_all=True) or []
    
    @staticmethod
    def get_all_categories():
        """Get all categories (for admin)"""
        query = """
            SELECT id, name, description, image_url, is_active, created_at
            FROM categories
            ORDER BY created_at DESC
        """
        return execute_dict_query(query, fetch_all=True) or []
    
    @staticmethod
    def get_by_id(category_id):
        """Get category by ID"""
        query = "SELECT * FROM categories WHERE id = %s"
        return execute_dict_query(query, (category_id,), fetch_one=True)
    
    @staticmethod
    def update(category_id, name=None, description=None, image_url=None, is_active=None):
        """Update category"""
        try:
            update_fields = []
            params = []
            
            if name is not None:
                update_fields.append("name = %s")
                params.append(name)
            if description is not None:
                update_fields.append("description = %s")
                params.append(description)
            if image_url is not None:
                update_fields.append("image_url = %s")
                params.append(image_url)
            if is_active is not None:
                update_fields.append("is_active = %s")
                params.append(is_active)
            
            if not update_fields:
                return False
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(category_id)
            
            query = f"UPDATE categories SET {', '.join(update_fields)} WHERE id = %s"
            result = execute_query(query, tuple(params), commit=True)
            return result > 0 if result else False
        except Exception as e:
            logger.error(f"Error updating category: {str(e)}")
            return False
    
    @staticmethod
    def delete(category_id):
        """Soft delete category"""
        query = "UPDATE categories SET is_active = FALSE WHERE id = %s"
        result = execute_query(query, (category_id,), commit=True)
        return result > 0 if result else False