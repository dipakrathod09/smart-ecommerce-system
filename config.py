"""
Configuration file for Smart E-Commerce System
Contains all application settings and configurations
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # ===================================================================
    # FLASK SETTINGS
    # ===================================================================
    
    # Secret key for session encryption (CHANGE THIS IN PRODUCTION!)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-2025'
    
    # Session configuration
    SESSION_COOKIE_NAME = 'smart_ecommerce_session'
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)  # Session expires after 24 hours
    
    # ===================================================================
    # DATABASE SETTINGS
    # ===================================================================
    
    # PostgreSQL connection details
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    DB_NAME = 'smart_ecommerce_db'
    DB_USER = 'postgres'
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Admin@123')  # Set DB_PASSWORD env var in production!
    
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
    
    # In production, these should come from environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')


class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG = True
    TESTING = True
    DB_NAME = 'smart_ecommerce_test_db'


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
