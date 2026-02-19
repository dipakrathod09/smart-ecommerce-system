"""
Configuration file for Smart E-Commerce System
Contains all application settings and configurations
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    
    # ===================================================================
    # FLASK SETTINGS
    # ===================================================================
    
    # Secret key for session encryption — MUST be set in .env or environment
    # Application will crash on startup if this is missing (intentional safety measure)
    SECRET_KEY = os.environ['SECRET_KEY']
    
    # Session configuration
    SESSION_COOKIE_NAME = 'smart_ecommerce_session'
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)  # Session expires after 24 hours
    
    # ===================================================================
    # DATABASE SETTINGS
    # ===================================================================
    
    # PostgreSQL connection details — loaded from .env
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'smart_ecommerce_db')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    
    # Connection pool settings
    DB_MIN_CONN = 1
    DB_MAX_CONN = 10
    
    # ===================================================================
    # FILE UPLOAD SETTINGS
    # ===================================================================
    
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static/images/products')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # ===================================================================
    # PAGINATION SETTINGS
    # ===================================================================
    
    PRODUCTS_PER_PAGE = 12
    ORDERS_PER_PAGE = 10
    USERS_PER_PAGE = 20
    
    # ===================================================================
    # INVENTORY SETTINGS
    # ===================================================================
    
    LOW_STOCK_THRESHOLD = 10  # Alert when stock falls below this
    OUT_OF_STOCK_THRESHOLD = 0
    
    # ===================================================================
    # ORDER SETTINGS
    # ===================================================================
    
    # Available order statuses
    ORDER_STATUSES = [
        'Pending',
        'Confirmed',
        'Processing',
        'Shipped',
        'Delivered',
        'Cancelled'
    ]
    
    # Available payment methods
    PAYMENT_METHODS = [
        'COD',      # Cash on Delivery
        'Card',     # Debit/Credit Card
        'UPI'       # UPI Payment
    ]
    
    # Payment status options
    PAYMENT_STATUSES = [
        'Pending',
        'Success',
        'Failed',
        'Refunded'
    ]
    
    # ===================================================================
    # RECOMMENDATION SETTINGS
    # ===================================================================
    
    # Number of recommendations to show
    RECOMMENDATIONS_COUNT = 8
    
    # Weights for hybrid recommendation algorithm
    RECOMMENDATION_WEIGHTS = {
        'purchase_history': 0.4,   # 40% weight
        'category_based': 0.3,     # 30% weight
        'popular': 0.2,            # 20% weight
        'best_selling': 0.1        # 10% weight
    }
    
    # ===================================================================
    # ANALYTICS SETTINGS
    # ===================================================================
    
    ANALYTICS_DAYS_RANGE = 30  # Default days for analytics
    TOP_PRODUCTS_COUNT = 10    # Top N products in reports
    
    # ===================================================================
    # SECURITY SETTINGS
    # ===================================================================
    
    # Bcrypt rounds for password hashing (higher = more secure but slower)
    BCRYPT_LOG_ROUNDS = 12
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 6
    
    # ===================================================================
    # ENVIRONMENT-SPECIFIC SETTINGS
    # ===================================================================
    
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    
    # SECRET_KEY is already enforced by the base Config class
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    SESSION_COOKIE_SECURE = True  # HTTPS only in production


class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG = True
    TESTING = True
    SECRET_KEY = 'test-secret-key-not-for-production'  # Fixed key for test determinism
    DB_NAME = 'smart_ecommerce_test_db'
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """
    Get configuration based on environment variable
    Returns development config by default
    """
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
