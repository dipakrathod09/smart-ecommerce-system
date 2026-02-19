"""
Product Service
Handles business logic for product management, search, and filtering.
Separates logic from data access (Product model).
"""

import logging
from models.product import Product
from models.category import Category

logger = logging.getLogger(__name__)

class ProductService:
    """Service for managing products"""
    
    @staticmethod
    def get_product_by_id(product_id):
        """Get product by ID"""
        return Product.get_by_id(product_id)

    @staticmethod
    def get_products(page=1, per_page=12, category_id=None, search_term=None, 
                    min_price=None, max_price=None, sort_by='created_at', sort_order='DESC',
                    include_inactive=False):
        """Get all products with filtering"""
        return Product.get_all(
            page=page, 
            per_page=per_page, 
            category_id=category_id, 
            search_term=search_term,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            sort_order=sort_order,
            include_inactive=include_inactive
        )

    @staticmethod
    def get_total_count(category_id=None, search_term=None):
        """Get total product count for pagination"""
        return Product.get_total_count(category_id, search_term)

    @staticmethod
    def create_product(category_id, name, description, price, stock, brand=None, image_url=None):
        """Create a new product"""
        # Business logic: Validation could go here
        if price < 0:
            logger.warning("Attempted to create product with negative price")
            return None
            
        return Product.create(category_id, name, description, price, stock, brand, image_url)

    @staticmethod
    def update_product(product_id, **kwargs):
        """Update product details"""
        # Business logic: validate price if present
        if 'price' in kwargs and kwargs['price'] is not None and kwargs['price'] < 0:
            logger.warning("Attempted to update product with negative price")
            return False
            
        return Product.update(product_id, **kwargs)

    @staticmethod
    def delete_product(product_id):
        """
        Hard delete product and clean up dependencies
        """
        try:
            # 1. Clean up dependencies first
            from models.cart import Cart
            from models.wishlist import Wishlist
            from models.review import Review
            
            Cart.delete_by_product(product_id)
            Wishlist.delete_by_product(product_id)
            Review.delete_by_product(product_id)
            
            # 2. Attempt hard delete
            # If this fails (e.g. Foreign Key constraint from order_items), it returns False
            return Product.delete(product_id)
            
        except Exception as e:
            logger.error(f"Error in delete_product service: {str(e)}")
            return False

    @staticmethod
    def get_related_products(product_id, limit=4):
        """Get related products"""
        return Product.get_related_products(product_id, limit)

    @staticmethod
    def get_featured_products(limit=8):
        """Get featured products"""
        return Product.get_featured_products(limit)
    
    @staticmethod
    def get_search_suggestions(query, limit=8):
        """Get search suggestions"""
        return Product.get_search_suggestions(query, limit)

    @staticmethod
    def check_stock(product_id, required_quantity):
        """Check if sufficient stock available"""
        return Product.check_stock(product_id, required_quantity)

    @staticmethod
    def update_stock(product_id, quantity_change):
        """Update product stock"""
        return Product.update_stock(product_id, quantity_change)
