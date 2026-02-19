"""
User Model
Handles user registration, authentication, and profile management
"""


from database.db_connection import execute_query, execute_dict_query
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class User:
    """User model for customer accounts"""
    

    
    
    @staticmethod
    def create(full_name, email, password_hash, phone=None, address=None, 
                 city=None, state=None, pincode=None):
        """
        Create a new user in database
        """
        try:
            query = """
                INSERT INTO users (full_name, email, password_hash, phone, 
                                 address, city, state, pincode)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, full_name, email, created_at
            """
            
            result = execute_dict_query(
                query,
                (full_name, email, password_hash, phone, address, city, state, pincode),
                fetch_one=True
            )
            
            if result:
                logger.info(f"User created: {email}")
                return result
            return None
                
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None
    
    
    @staticmethod
    def get_user_with_credentials(email):
        """
        Get user by email including password hash (for internal auth only)
        """
        try:
            query = """
                SELECT id, full_name, email, password_hash, is_active
                FROM users
                WHERE email = %s
            """
            return execute_dict_query(query, (email,), fetch_one=True)
        except Exception as e:
            logger.error(f"Error fetching credentials: {str(e)}")
            return None
    
    
    @staticmethod
    def email_exists(email):
        """
        Check if email already exists in database
        
        Args:
            email (str): Email to check
            
        Returns:
            bool: True if exists, False otherwise
        """
        query = "SELECT COUNT(*) FROM users WHERE email = %s"
        result = execute_query(query, (email,), fetch_one=True)
        return result[0] > 0 if result else False
    
    
    @staticmethod
    def get_by_id(user_id):
        """
        Get user by ID
        
        Args:
            user_id (int): User ID
            
        Returns:
            dict: User data without password hash
        """
        query = """
            SELECT id, full_name, email, phone, address, city, state, pincode,
                   created_at, is_active, last_login
            FROM users
            WHERE id = %s
        """
        return execute_dict_query(query, (user_id,), fetch_one=True)
    
    
    @staticmethod
    def get_by_email(email):
        """
        Get user by email
        
        Args:
            email (str): User email
            
        Returns:
            dict: User data without password hash
        """
        query = """
            SELECT id, full_name, email, phone, address, city, state, pincode,
                   created_at, is_active, last_login
            FROM users
            WHERE email = %s
        """
        return execute_dict_query(query, (email,), fetch_one=True)
    
    
    @staticmethod
    def update_profile(user_id, full_name=None, phone=None, address=None,
                      city=None, state=None, pincode=None):
        """
        Update user profile
        
        Args:
            user_id (int): User ID
            full_name (str): Updated full name
            phone (str): Updated phone
            address (str): Updated address
            city (str): Updated city
            state (str): Updated state
            pincode (str): Updated pincode
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Build dynamic update query based on provided fields
            update_fields = []
            params = []
            
            if full_name is not None:
                update_fields.append("full_name = %s")
                params.append(full_name)
            
            if phone is not None:
                update_fields.append("phone = %s")
                params.append(phone)
            
            if address is not None:
                update_fields.append("address = %s")
                params.append(address)
            
            if city is not None:
                update_fields.append("city = %s")
                params.append(city)
            
            if state is not None:
                update_fields.append("state = %s")
                params.append(state)
            
            if pincode is not None:
                update_fields.append("pincode = %s")
                params.append(pincode)
            
            if not update_fields:
                return False
            
            # Add user_id to params
            params.append(user_id)
            
            query = f"""
                UPDATE users
                SET {', '.join(update_fields)}
                WHERE id = %s
            """
            
            result = execute_query(query, tuple(params), commit=True)
            
            if result and result > 0:
                logger.info(f"Profile updated for user ID: {user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            return False
    
    
    @staticmethod
    def get_password_hash(user_id):
        """Get password hash for a user"""
        query = "SELECT password_hash FROM users WHERE id = %s"
        result = execute_query(query, (user_id,), fetch_one=True)
        return result[0] if result else None

    @staticmethod
    def update_password_hash(user_id, new_password_hash):
        """Update password hash"""
        try:
            query = "UPDATE users SET password_hash = %s WHERE id = %s"
            result = execute_query(query, (new_password_hash, user_id), commit=True)
            return result > 0 if result else False
        except Exception as e:
            logger.error(f"Error updating password hash: {str(e)}")
            return False
    
    
    @staticmethod
    def update_last_login(user_id):
        """
        Update user's last login timestamp
        
        Args:
            user_id (int): User ID
        """
        query = "UPDATE users SET last_login = %s WHERE id = %s"
        execute_query(query, (datetime.now(), user_id), commit=True)
    
    
    @staticmethod
    def deactivate(user_id):
        """
        Deactivate user account
        
        Args:
            user_id (int): User ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = "UPDATE users SET is_active = FALSE WHERE id = %s"
        result = execute_query(query, (user_id,), commit=True)
        return result > 0 if result else False
    
    
    @staticmethod
    def activate(user_id):
        """
        Activate user account
        
        Args:
            user_id (int): User ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = "UPDATE users SET is_active = TRUE WHERE id = %s"
        result = execute_query(query, (user_id,), commit=True)
        return result > 0 if result else False
    
    
    @staticmethod
    def get_all_users(page=1, per_page=20):
        """
        Get all users with pagination (for admin)
        
        Args:
            page (int): Page number
            per_page (int): Items per page
            
        Returns:
            list: List of user dictionaries
        """
        offset = (page - 1) * per_page
        
        query = """
            SELECT id, full_name, email, phone, city, state, 
                   created_at, is_active, last_login
            FROM users
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        
        return execute_dict_query(query, (per_page, offset), fetch_all=True) or []
    
    
    @staticmethod
    def get_total_count():
        """
        Get total number of users
        
        Returns:
            int: Total user count
        """
        query = "SELECT COUNT(*) FROM users"
        result = execute_query(query, fetch_one=True)
        return result[0] if result else 0
    
    
    @staticmethod
    def search_users(search_term, page=1, per_page=20):
        """
        Search users by name or email
        
        Args:
            search_term (str): Search term
            page (int): Page number
            per_page (int): Items per page
            
        Returns:
            list: List of matching user dictionaries
        """
        offset = (page - 1) * per_page
        search_pattern = f"%{search_term}%"
        
        query = """
            SELECT id, full_name, email, phone, city, state, 
                   created_at, is_active, last_login
            FROM users
            WHERE full_name ILIKE %s OR email ILIKE %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        
        return execute_dict_query(
            query,
            (search_pattern, search_pattern, per_page, offset),
            fetch_all=True
        ) or []
