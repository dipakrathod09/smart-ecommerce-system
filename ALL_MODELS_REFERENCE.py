"""
ALL MODELS IN ONE FILE
This file contains all the remaining models for easy reference.
In actual implementation, each model should be in its separate file.

MODELS INCLUDED:
1. Category Model
2. Cart Model
3. Order Model
4. Payment Model
5. Recommendation Model
6. Analytics Model
7. Admin Model
"""

from database.db_connection import execute_query, execute_dict_query
import logging
from datetime import datetime, timedelta
import random
import string

logger = logging.getLogger(__name__)

# ===================================================================
# CATEGORY MODEL
# File: models/category.py
# ===================================================================

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


# ===================================================================
# CART MODEL
# File: models/cart.py
# ===================================================================

class Cart:
    """Shopping cart model"""
    
    @staticmethod
    def add_item(user_id, product_id, quantity=1):
        """Add item to cart or update quantity if exists"""
        try:
            # Check if item already in cart
            check_query = "SELECT id, quantity FROM cart WHERE user_id = %s AND product_id = %s"
            existing = execute_dict_query(check_query, (user_id, product_id), fetch_one=True)
            
            if existing:
                # Update quantity
                new_quantity = existing['quantity'] + quantity
                update_query = "UPDATE cart SET quantity = %s WHERE id = %s"
                result = execute_query(update_query, (new_quantity, existing['id']), commit=True)
                return result > 0 if result else False
            else:
                # Insert new item
                insert_query = """
                    INSERT INTO cart (user_id, product_id, quantity)
                    VALUES (%s, %s, %s)
                """
                result = execute_query(insert_query, (user_id, product_id, quantity), commit=True)
                return result > 0 if result else False
        except Exception as e:
            logger.error(f"Error adding to cart: {str(e)}")
            return False
    
    @staticmethod
    def get_cart_items(user_id):
        """Get all cart items for user with product details"""
        query = """
            SELECT c.id as cart_id, c.quantity, c.added_at,
                   p.id as product_id, p.name, p.price, p.stock, 
                   p.image_url, p.brand,
                   (c.quantity * p.price) as subtotal
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s AND p.is_active = TRUE
            ORDER BY c.added_at DESC
        """
        return execute_dict_query(query, (user_id,), fetch_all=True) or []
    
    @staticmethod
    def get_cart_total(user_id):
        """Get total amount of cart"""
        query = """
            SELECT SUM(c.quantity * p.price) as total
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s AND p.is_active = TRUE
        """
        result = execute_query(query, (user_id,), fetch_one=True)
        return float(result[0]) if result and result[0] else 0.0
    
    @staticmethod
    def get_cart_count(user_id):
        """Get number of items in cart"""
        query = "SELECT COUNT(*) FROM cart WHERE user_id = %s"
        result = execute_query(query, (user_id,), fetch_one=True)
        return result[0] if result else 0
    
    @staticmethod
    def update_quantity(cart_id, quantity):
        """Update cart item quantity"""
        query = "UPDATE cart SET quantity = %s WHERE id = %s"
        result = execute_query(query, (quantity, cart_id), commit=True)
        return result > 0 if result else False
    
    @staticmethod
    def remove_item(cart_id):
        """Remove item from cart"""
        query = "DELETE FROM cart WHERE id = %s"
        result = execute_query(query, (cart_id,), commit=True)
        return result > 0 if result else False
    
    @staticmethod
    def clear_cart(user_id):
        """Clear all items from user's cart"""
        query = "DELETE FROM cart WHERE user_id = %s"
        result = execute_query(query, (user_id,), commit=True)
        return result > 0 if result else False


# ===================================================================
# ORDER MODEL
# File: models/order.py
# ===================================================================

class Order:
    """Order management model"""
    
    @staticmethod
    def generate_order_number():
        """Generate unique order number"""
        date_part = datetime.now().strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"ORD{date_part}{random_part}"
    
    @staticmethod
    def create_order(user_id, total_amount, shipping_address, shipping_city,
                    shipping_state, shipping_pincode, contact_phone):
        """Create a new order"""
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
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            return None
    
    @staticmethod
    def add_order_items(order_id, cart_items):
        """Add items to order from cart"""
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
        """Get order by ID with user details"""
        query = """
            SELECT o.*, u.full_name as customer_name, u.email as customer_email
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.id = %s
        """
        return execute_dict_query(query, (order_id,), fetch_one=True)
    
    @staticmethod
    def get_order_items(order_id):
        """Get items for an order"""
        query = """
            SELECT * FROM order_items
            WHERE order_id = %s
            ORDER BY id
        """
        return execute_dict_query(query, (order_id,), fetch_all=True) or []
    
    @staticmethod
    def get_user_orders(user_id, page=1, per_page=10):
        """Get orders for a user with pagination"""
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
        """Get all orders (for admin)"""
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
        """Update order status"""
        query = "UPDATE orders SET order_status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
        result = execute_query(query, (new_status, order_id), commit=True)
        
        if result and result > 0:
            logger.info(f"Order {order_id} status updated to {new_status}")
            return True
        return False
    
    @staticmethod
    def get_order_count():
        """Get total order count"""
        query = "SELECT COUNT(*) FROM orders"
        result = execute_query(query, fetch_one=True)
        return result[0] if result else 0


# ===================================================================
# PAYMENT MODEL
# File: models/payment.py
# ===================================================================

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
            
            # Simulate payment success (90% success rate)
            payment_status = 'Success' if random.random() < 0.9 else 'Failed'
            
            query = """
                INSERT INTO payments (order_id, transaction_id, payment_method, 
                                    amount, payment_status, card_last_four, upi_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, transaction_id, payment_status
            """
            
            result = execute_dict_query(
                query,
                (order_id, transaction_id, payment_method, amount, 
                 payment_status, card_last_four, upi_id),
                fetch_one=True
            )
            
            if result and result['payment_status'] == 'Success':
                # Update order status
                from models.order import Order
                Order.update_status(order_id, 'Confirmed')
                logger.info(f"Payment successful: {transaction_id}")
            else:
                logger.warning(f"Payment failed: {transaction_id}")
            
            return result
        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}")
            return None
    
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


# ===================================================================
# RECOMMENDATION MODEL
# File: models/recommendation.py
# ===================================================================

class Recommendation:
    """Rule-based recommendation engine"""
    
    @staticmethod
    def get_purchase_history_recommendations(user_id, limit=8):
        """Recommend products based on user's purchase history"""
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
        """Recommend products from same category"""
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
        """Get popular/best-selling products"""
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
        """Hybrid recommendation combining multiple strategies"""
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
        
        # Remove duplicates and limit
        seen_ids = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec['id'] not in seen_ids:
                seen_ids.add(rec['id'])
                unique_recommendations.append(rec)
                if len(unique_recommendations) >= limit:
                    break
        
        return unique_recommendations


# ===================================================================
# ANALYTICS MODEL
# File: models/analytics.py
# ===================================================================

class Analytics:
    """Analytics and reporting model"""
    
    @staticmethod
    def get_total_revenue():
        """Get total revenue from all orders"""
        query = """
            SELECT COALESCE(SUM(total_amount), 0) as total_revenue
            FROM orders
            WHERE order_status != 'Cancelled'
        """
        result = execute_query(query, fetch_one=True)
        return float(result[0]) if result else 0.0
    
    @staticmethod
    def get_total_orders():
        """Get total number of orders"""
        query = "SELECT COUNT(*) FROM orders WHERE order_status != 'Cancelled'"
        result = execute_query(query, fetch_one=True)
        return result[0] if result else 0
    
    @staticmethod
    def get_daily_sales(days=30):
        """Get daily sales for last N days"""
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
        """Get monthly sales for last N months"""
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
        """Get best-selling products"""
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
        """Get sales by category"""
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
        """Get payment method distribution"""
        query = """
            SELECT payment_method,
                   COUNT(*) as transaction_count,
                   SUM(amount) as total_amount
            FROM payments
            WHERE payment_status = 'Success'
            GROUP BY payment_method
            ORDER BY transaction_count DESC
        """
        return execute_dict_query(query, fetch_all=True) or []
    
    @staticmethod
    def get_low_stock_products(threshold=10):
        """Get products with low stock"""
        from models.product import Product
        return Product.get_low_stock_products(threshold)
    
    @staticmethod
    def get_dashboard_stats():
        """Get overall dashboard statistics"""
        return {
            'total_revenue': Analytics.get_total_revenue(),
            'total_orders': Analytics.get_total_orders(),
            'total_users': Analytics.get_total_users(),
            'total_products': Analytics.get_total_products(),
            'low_stock_count': len(Analytics.get_low_stock_products())
        }
    
    @staticmethod
    def get_total_users():
        """Get total number of users"""
        query = "SELECT COUNT(*) FROM users WHERE is_active = TRUE"
        result = execute_query(query, fetch_one=True)
        return result[0] if result else 0
    
    @staticmethod
    def get_total_products():
        """Get total number of products"""
        query = "SELECT COUNT(*) FROM products WHERE is_active = TRUE"
        result = execute_query(query, fetch_one=True)
        return result[0] if result else 0


# ===================================================================
# ADMIN MODEL
# File: models/admin.py
# ===================================================================

class Admin:
    """Admin model for administrator operations"""
    
    @staticmethod
    def hash_password(password):
        """Hash password using bcrypt"""
        import bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password, hashed_password):
        """Verify password"""
        import bcrypt
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except:
            return False
    
    @staticmethod
    def login(username, password):
        """Admin login"""
        try:
            query = """
                SELECT id, username, password_hash, email, full_name, is_super_admin
                FROM admin
                WHERE username = %s
            """
            admin = execute_dict_query(query, (username,), fetch_one=True)
            
            if not admin:
                logger.warning(f"Admin login failed: User not found - {username}")
                return None
            
            if Admin.verify_password(password, admin['password_hash']):
                # Update last login
                update_query = "UPDATE admin SET last_login = %s WHERE id = %s"
                execute_query(update_query, (datetime.now(), admin['id']), commit=True)
                
                del admin['password_hash']
                logger.info(f"Admin logged in: {username}")
                return admin
            else:
                logger.warning(f"Admin login failed: Invalid password - {username}")
                return None
        except Exception as e:
            logger.error(f"Error during admin login: {str(e)}")
            return None
    
    @staticmethod
    def get_by_id(admin_id):
        """Get admin by ID"""
        query = """
            SELECT id, username, email, full_name, is_super_admin, created_at, last_login
            FROM admin
            WHERE id = %s
        """
        return execute_dict_query(query, (admin_id,), fetch_one=True)
