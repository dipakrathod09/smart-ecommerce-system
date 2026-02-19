from database.db_connection import execute_query, execute_dict_query
import logging

logger = logging.getLogger(__name__)


class Cart:
    """Shopping cart model"""

    # ==========================================================
    # ADD ITEM TO CART
    # ==========================================================
    @staticmethod
    def add_item(user_id, product_id, quantity=1):
        """Add item to cart or update quantity if already exists"""
        try:
            if quantity <= 0:
                return False

            # Check product stock and active status
            product_query = """
                SELECT stock 
                FROM products 
                WHERE id = %s AND is_active = TRUE
            """
            product = execute_dict_query(product_query, (product_id,), fetch_one=True)

            if not product:
                return False

            # Check if item already exists in cart
            check_query = """
                SELECT id, quantity 
                FROM cart 
                WHERE user_id = %s AND product_id = %s
            """
            existing = execute_dict_query(
                check_query, (user_id, product_id), fetch_one=True
            )

            if existing:
                new_quantity = existing["quantity"] + quantity

                if new_quantity > product["stock"]:
                    return False

                update_query = """
                    UPDATE cart 
                    SET quantity = %s 
                    WHERE id = %s
                """
                execute_query(update_query, (new_quantity, existing["id"]), commit=True)
                return True

            else:
                if quantity > product["stock"]:
                    return False

                insert_query = """
                    INSERT INTO cart (user_id, product_id, quantity)
                    VALUES (%s, %s, %s)
                """
                execute_query(
                    insert_query, (user_id, product_id, quantity), commit=True
                )
                return True

        except Exception as e:
            logger.error(f"Error adding item to cart: {e}")
            return False

    # ==========================================================
    # GET CART ITEMS
    # ==========================================================
    @staticmethod
    def get_cart_items(user_id):
        """Get all cart items with product details"""
        query = """
            SELECT 
                c.id AS cart_id,
                c.quantity,
                c.added_at,
                p.id AS product_id,
                p.name,
                p.price,
                p.stock,
                p.image_url,
                p.brand,
                (c.quantity * p.price) AS subtotal
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s AND p.is_active = TRUE
            ORDER BY c.added_at DESC
        """
        return execute_dict_query(query, (user_id,), fetch_all=True) or []

    # ==========================================================
    # GET CART TOTAL
    # ==========================================================
    @staticmethod
    def get_cart_total(user_id):
        """Get total cart value"""
        query = """
            SELECT COALESCE(SUM(c.quantity * p.price), 0) AS total
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s AND p.is_active = TRUE
        """
        result = execute_dict_query(query, (user_id,), fetch_one=True)
        return float(result["total"]) if result else 0.0

    # ==========================================================
    # GET CART ITEM COUNT (BADGE COUNT)
    # ==========================================================
    @staticmethod
    def get_cart_count(user_id):
        """Get total quantity of items in cart"""
        query = """
            SELECT COALESCE(SUM(quantity), 0) AS count
            FROM cart
            WHERE user_id = %s
        """
        result = execute_dict_query(query, (user_id,), fetch_one=True)
        return result["count"] if result else 0

    # ==========================================================
    # UPDATE ITEM QUANTITY
    # ==========================================================
    @staticmethod
    def update_quantity(cart_id, quantity):
        """Update quantity of a cart item"""
        try:
            if quantity <= 0:
                return False

            # Get product stock for this cart item
            stock_query = """
                SELECT p.stock
                FROM cart c
                JOIN products p ON c.product_id = p.id
                WHERE c.id = %s
            """
            product = execute_dict_query(stock_query, (cart_id,), fetch_one=True)

            if not product or quantity > product["stock"]:
                return False

            update_query = """
                UPDATE cart 
                SET quantity = %s 
                WHERE id = %s
            """
            execute_query(update_query, (quantity, cart_id), commit=True)
            return True

        except Exception as e:
            logger.error(f"Error updating cart quantity: {e}")
            return False

    # ==========================================================
    # REMOVE ITEM FROM CART
    # ==========================================================
    @staticmethod
    def remove_item(cart_id):
        """Remove a single item from cart"""
        try:
            query = "DELETE FROM cart WHERE id = %s"
            execute_query(query, (cart_id,), commit=True)
            return True
        except Exception as e:
            logger.error(f"Error removing cart item: {e}")
            return False

    # ==========================================================
    # CLEAR USER CART
    # ==========================================================
    @staticmethod
    def clear_cart(user_id):
        """Remove all items from user's cart"""
        try:
            query = "DELETE FROM cart WHERE user_id = %s"
            execute_query(query, (user_id,), commit=True)
            return True
        except Exception as e:
            logger.error(f"Error clearing cart: {e}")
            return False

    @staticmethod
    def delete_by_product(product_id):
        """
        Remove a product from all carts (before delete)
        
        Args:
            product_id (int): Product ID
            
        Returns:
            bool: True if successful
        """
        try:
            query = "DELETE FROM cart WHERE product_id = %s"
            execute_query(query, (product_id,), commit=True)
            return True
        except Exception as e:
            logger.error(f"Error removing product {product_id} from carts: {e}")
            return False
