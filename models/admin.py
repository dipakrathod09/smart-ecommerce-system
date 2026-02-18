"""
Admin Model
Handles admin authentication and operations
"""

import bcrypt
from database.db_connection import execute_query, execute_dict_query
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Admin:
    """Admin model for administrator operations"""
    
    @staticmethod
    def hash_password(password):
        """
        Hash password using bcrypt
        
        Args:
            password (str): Plain text password
            
        Returns:
            str: Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    
    @staticmethod
    def verify_password(plain_password, hashed_password):
        """
        Verify password against hash
        
        Args:
            plain_password (str): Password to verify
            hashed_password (str): Hashed password from database
            
        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False
    
    
    @staticmethod
    def login(username, password):
        """
        Admin login authentication
        
        Args:
            username (str): Admin username
            password (str): Admin password
            
        Returns:
            dict: Admin data if authentication successful, None otherwise
        """
        try:
            query = """
                SELECT id, username, password_hash, email, full_name, is_super_admin
                FROM admin
                WHERE username = %s OR email = %s
            """
            
            admin = execute_dict_query(query, (username, username), fetch_one=True)
            
            if not admin:
                logger.warning(f"Admin login failed: User not found - {username}")
                return None
            
            # Verify password
            if Admin.verify_password(password, admin['password_hash']):
                # Update last login
                update_query = "UPDATE admin SET last_login = %s WHERE id = %s"
                execute_query(update_query, (datetime.now(), admin['id']), commit=True)
                
                # Remove password hash from returned data
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
        """
        Get admin by ID
        
        Args:
            admin_id (int): Admin ID
            
        Returns:
            dict: Admin data without password hash
        """
        query = """
            SELECT id, username, email, full_name, is_super_admin, created_at, last_login
            FROM admin
            WHERE id = %s
        """
        return execute_dict_query(query, (admin_id,), fetch_one=True)
    
    
    @staticmethod
    def create_admin(username, password, email, full_name=None, is_super_admin=False):
        """
        Create a new admin account
        
        Args:
            username (str): Admin username
            password (str): Admin password
            email (str): Admin email
            full_name (str): Admin full name (optional)
            is_super_admin (bool): Super admin status
            
        Returns:
            dict: Created admin data or None
        """
        try:
            # Check if username already exists
            check_query = "SELECT COUNT(*) FROM admin WHERE username = %s"
            result = execute_query(check_query, (username,), fetch_one=True)
            
            if result and result[0] > 0:
                logger.warning(f"Admin creation failed: Username {username} already exists")
                return None
            
            # Hash password
            password_hash = Admin.hash_password(password)
            
            # Insert admin
            query = """
                INSERT INTO admin (username, password_hash, email, full_name, is_super_admin)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, username, email, created_at
            """
            
            admin = execute_dict_query(
                query,
                (username, password_hash, email, full_name, is_super_admin),
                fetch_one=True
            )
            
            if admin:
                logger.info(f"Admin created: {username}")
                return admin
            return None
            
        except Exception as e:
            logger.error(f"Error creating admin: {str(e)}")
            return None
    
    
    @staticmethod
    def update_password(admin_id, current_password, new_password):
        """
        Update admin password
        
        Args:
            admin_id (int): Admin ID
            current_password (str): Current password for verification
            new_password (str): New password to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get current password hash
            query = "SELECT password_hash FROM admin WHERE id = %s"
            result = execute_query(query, (admin_id,), fetch_one=True)
            
            if not result:
                return False
            
            # Verify current password
            if not Admin.verify_password(current_password, result[0]):
                logger.warning(f"Admin password update failed: Incorrect current password")
                return False
            
            # Hash new password
            new_password_hash = Admin.hash_password(new_password)
            
            # Update password
            update_query = "UPDATE admin SET password_hash = %s WHERE id = %s"
            update_result = execute_query(
                update_query,
                (new_password_hash, admin_id),
                commit=True
            )
            
            if update_result and update_result > 0:
                logger.info(f"Admin password updated: ID {admin_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error updating admin password: {str(e)}")
            return False
    
    
    @staticmethod
    def get_all_admins():
        """
        Get all admin accounts
        
        Returns:
            list: List of admin dictionaries
        """
        query = """
            SELECT id, username, email, full_name, is_super_admin, created_at, last_login
            FROM admin
            ORDER BY created_at DESC
        """
        return execute_dict_query(query, fetch_all=True) or []
