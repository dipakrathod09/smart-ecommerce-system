"""
Product Model
Handles product CRUD operations, search, filtering, and inventory management
"""

from database.db_connection import execute_query, execute_dict_query
import logging

logger = logging.getLogger(__name__)


class Product:
    """Product model for managing product catalog"""
    
    @staticmethod
    def create(category_id, name, description, price, stock, brand=None, image_url=None):
        """
        Create a new product
        
        Args:
            category_id (int): Category ID
            name (str): Product name
            description (str): Product description
            price (float): Product price
            stock (int): Stock quantity
            brand (str): Brand name (optional)
            image_url (str): Image URL (optional)
            
        Returns:
            dict: Created product data or None
        """
        try:
            query = """
                INSERT INTO products (category_id, name, description, price, stock, brand, image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, name, price, stock, created_at
            """
            
            result = execute_dict_query(
                query,
                (category_id, name, description, price, stock, brand, image_url),
                fetch_one=True
            )
            
            if result:
                logger.info(f"Product created: {name}")
                return result
            return None
            
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            return None
    
    
    @staticmethod
    def get_by_id(product_id):
        """
        Get product by ID with category name
        
        Args:
            product_id (int): Product ID
            
        Returns:
            dict: Product data with category information
        """
        query = """
            SELECT p.*, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.id = %s
        """
        return execute_dict_query(query, (product_id,), fetch_one=True)
    
    
    @staticmethod
    def get_all(page=1, per_page=12, category_id=None, search_term=None, 
                min_price=None, max_price=None, sort_by='created_at', sort_order='DESC'):
        """
        Get all products with filtering, search, and pagination
        
        Args:
            page (int): Page number
            per_page (int): Items per page
            category_id (int): Filter by category (optional)
            search_term (str): Search in product name (optional)
            min_price (float): Minimum price filter (optional)
            max_price (float): Maximum price filter (optional)
            sort_by (str): Sort column (name, price, created_at)
            sort_order (str): ASC or DESC
            
        Returns:
            list: List of product dictionaries
        """
        offset = (page - 1) * per_page
        
        # Build WHERE clause dynamically
        where_clauses = ["p.is_active = TRUE"]
        params = []
        
        if category_id:
            where_clauses.append("p.category_id = %s")
            params.append(category_id)
        
        if search_term:
            where_clauses.append("(p.name ILIKE %s OR p.description ILIKE %s)")
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern])
        
        if min_price is not None:
            where_clauses.append("p.price >= %s")
            params.append(min_price)
        
        if max_price is not None:
            where_clauses.append("p.price <= %s")
            params.append(max_price)
        
        where_clause = " AND ".join(where_clauses)
        
        # Validate sort parameters
        valid_sort_columns = ['name', 'price', 'created_at', 'stock']
        if sort_by not in valid_sort_columns:
            sort_by = 'created_at'
        
        if sort_order.upper() not in ['ASC', 'DESC']:
            sort_order = 'DESC'
        
        query = f"""
            SELECT p.*, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE {where_clause}
            ORDER BY p.{sort_by} {sort_order}
            LIMIT %s OFFSET %s
        """
        
        params.extend([per_page, offset])
        
        return execute_dict_query(query, tuple(params), fetch_all=True) or []
    
    
    @staticmethod
    def get_by_category(category_id, limit=12):
        """
        Get products by category
        
        Args:
            category_id (int): Category ID
            limit (int): Maximum number of products
            
        Returns:
            list: List of products
        """
        query = """
            SELECT p.*, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.category_id = %s AND p.is_active = TRUE
            ORDER BY p.created_at DESC
            LIMIT %s
        """
        return execute_dict_query(query, (category_id, limit), fetch_all=True) or []
    
    
    @staticmethod
    def get_featured_products(limit=8):
        """
        Get featured/latest products for home page
        
        Args:
            limit (int): Number of products to fetch
            
        Returns:
            list: List of products
        """
        query = """
            SELECT p.*, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.is_active = TRUE AND p.stock > 0
            ORDER BY p.created_at DESC
            LIMIT %s
        """
        return execute_dict_query(query, (limit,), fetch_all=True) or []
    
    
    @staticmethod
    def update(product_id, category_id=None, name=None, description=None,
               price=None, stock=None, brand=None, image_url=None, is_active=None):
        """
        Update product details
        
        Args:
            product_id (int): Product ID
            category_id (int): Updated category ID
            name (str): Updated name
            description (str): Updated description
            price (float): Updated price
            stock (int): Updated stock
            brand (str): Updated brand
            image_url (str): Updated image URL
            is_active (bool): Updated active status
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            update_fields = []
            params = []
            
            if category_id is not None:
                update_fields.append("category_id = %s")
                params.append(category_id)
            
            if name is not None:
                update_fields.append("name = %s")
                params.append(name)
            
            if description is not None:
                update_fields.append("description = %s")
                params.append(description)
            
            if price is not None:
                update_fields.append("price = %s")
                params.append(price)
            
            if stock is not None:
                update_fields.append("stock = %s")
                params.append(stock)
            
            if brand is not None:
                update_fields.append("brand = %s")
                params.append(brand)
            
            if image_url is not None:
                update_fields.append("image_url = %s")
                params.append(image_url)
            
            if is_active is not None:
                update_fields.append("is_active = %s")
                params.append(is_active)
            
            if not update_fields:
                return False
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(product_id)
            
            query = f"""
                UPDATE products
                SET {', '.join(update_fields)}
                WHERE id = %s
            """
            
            result = execute_query(query, tuple(params), commit=True)
            
            if result and result > 0:
                logger.info(f"Product updated: ID {product_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            return False
    
    
    @staticmethod
    def delete(product_id):
        """
        Soft delete product (set is_active to False)
        
        Args:
            product_id (int): Product ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = "UPDATE products SET is_active = FALSE WHERE id = %s"
        result = execute_query(query, (product_id,), commit=True)
        
        if result and result > 0:
            logger.info(f"Product soft deleted: ID {product_id}")
            return True
        return False
    
    
    @staticmethod
    def update_stock(product_id, quantity_change):
        """
        Update product stock (increase or decrease)
        
        Args:
            product_id (int): Product ID
            quantity_change (int): Positive to add, negative to subtract
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = """
            UPDATE products
            SET stock = stock + %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND (stock + %s) >= 0
        """
        result = execute_query(
            query,
            (quantity_change, product_id, quantity_change),
            commit=True
        )
        return result > 0 if result else False
    
    
    @staticmethod
    def check_stock(product_id, required_quantity):
        """
        Check if sufficient stock is available
        
        Args:
            product_id (int): Product ID
            required_quantity (int): Required quantity
            
        Returns:
            bool: True if sufficient stock, False otherwise
        """
        query = "SELECT stock FROM products WHERE id = %s AND is_active = TRUE"
        result = execute_query(query, (product_id,), fetch_one=True)
        
        if result:
            return result[0] >= required_quantity
        return False
    
    
    @staticmethod
    def get_low_stock_products(threshold=10):
        """
        Get products with low stock (for admin alerts)
        
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
    def get_total_count(category_id=None, search_term=None):
        """
        Get total number of products (for pagination)
        
        Args:
            category_id (int): Filter by category (optional)
            search_term (str): Search term (optional)
            
        Returns:
            int: Total product count
        """
        where_clauses = ["is_active = TRUE"]
        params = []
        
        if category_id:
            where_clauses.append("category_id = %s")
            params.append(category_id)
        
        if search_term:
            where_clauses.append("(name ILIKE %s OR description ILIKE %s)")
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern])
        
        where_clause = " AND ".join(where_clauses)
        query = f"SELECT COUNT(*) FROM products WHERE {where_clause}"
        
        result = execute_query(query, tuple(params) if params else None, fetch_one=True)
        return result[0] if result else 0
    
    
    @staticmethod
    def get_related_products(product_id, limit=4):
        """
        Get related products from same category
        
        Args:
            product_id (int): Current product ID
            limit (int): Number of related products
            
        Returns:
            list: List of related products
        """
        query = """
            SELECT p.*, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.category_id = (SELECT category_id FROM products WHERE id = %s)
            AND p.id != %s
            AND p.is_active = TRUE
            AND p.stock > 0
            ORDER BY RANDOM()
            LIMIT %s
        """
        return execute_dict_query(query, (product_id, product_id, limit), fetch_all=True) or []


    @staticmethod
    def get_search_suggestions(query, limit=8):
        """
        Get product name suggestions for autocomplete
        
        Args:
            query (str): Search term
            limit (int): Maximum suggestions
            
        Returns:
            list: List of dictionaries {'id': int, 'name': str, 'image_url': str, 'price': float}
        """
        if not query or len(query) < 2:
            return []
            
        sql = """
            SELECT id, name, image_url, price, category_id
            FROM products 
            WHERE is_active = TRUE 
            AND (name ILIKE %s OR description ILIKE %s)
            ORDER BY 
                CASE WHEN name ILIKE %s THEN 0 ELSE 1 END,
                name ASC
            LIMIT %s
        """
        search_pattern = f"%{query}%"
        exact_start_pattern = f"{query}%"
        
        return execute_dict_query(sql, (search_pattern, search_pattern, exact_start_pattern, limit), fetch_all=True) or []
