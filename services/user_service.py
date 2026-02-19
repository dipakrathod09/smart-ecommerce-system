"""
User Service
Handles business logic for user registration, authentication, and profile management.
Separates logic from data access (User model).
"""

import bcrypt
import logging
from models.user import User

logger = logging.getLogger(__name__)

class UserService:
    """Service for managing users"""
    
    @staticmethod
    def hash_password(password):
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password, hashed_password):
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False

    @staticmethod
    def register_user(full_name, email, password, phone=None, address=None, 
                     city=None, state=None, pincode=None):
        """
        Register a new user
        Returns: (user_dict, error_message)
        """
        try:
            if User.email_exists(email):
                logger.warning(f"Registration failed: Email {email} already exists")
                return None, "Email address already registered. Please login or use another email."
            
            password_hash = UserService.hash_password(password)
            
            user = User.create(
                full_name, email, password_hash, phone, address, city, state, pincode
            )
            
            if user:
                logger.info(f"User registered successfully: {email}")
                return user, None
            
            return None, "Failed to create user account. Please contact support."
            
        except Exception as e:
            logger.error(f"Error in register_user service: {str(e)}")
            return None, f"An internal error occurred: {str(e)}"

    @staticmethod
    def authenticate_user(email, password):
        """
        Authenticate a user
        1. Get user by email
        2. Check if active
        3. Verify password
        4. Update last login
        """
        try:
            # We explicitly need the password_hash here
            user = User.get_user_with_credentials(email)
            
            if not user:
                logger.warning(f"Login failed: User not found - {email}")
                return None
            
            if not user['is_active']:
                logger.warning(f"Login failed: Account inactive - {email}")
                return None
            
            if UserService.verify_password(password, user['password_hash']):
                User.update_last_login(user['id'])
                
                # Remove sensitive data before returning
                del user['password_hash']
                return user
            
            logger.warning(f"Login failed: Invalid password - {email}")
            return None

        except Exception as e:
            logger.error(f"Error in authenticate_user service: {str(e)}")
            return None

    @staticmethod
    def change_password(user_id, current_password, new_password):
        """
        Change user password
        1. Verify current password
        2. Hash new password
        3. Update in DB
        """
        try:
            # Get current hash
            current_hash = User.get_password_hash(user_id)
            if not current_hash:
                return False

            if not UserService.verify_password(current_password, current_hash):
                logger.warning(f"Password change failed: Incorrect current password")
                return False

            new_hash = UserService.hash_password(new_password)
            return User.update_password_hash(user_id, new_hash)

        except Exception as e:
            logger.error(f"Error in change_password service: {str(e)}")
            return False
