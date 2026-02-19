import os
import pytest
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Set environment to testing BEFORE importing app/db
os.environ['FLASK_ENV'] = 'testing'

from app import app
from database.db_connection import get_db_connection, execute_query, close_all_connections
from config import config

# Get test config
test_config = config['testing']

@pytest.fixture(scope='session')
def app_instance():
    """Create application for the tests."""
    app.config.from_object(test_config)
    yield app
    # Teardown
    close_all_connections()

@pytest.fixture(scope='session')
def client(app_instance):
    """Create a test client for the app."""
    return app_instance.test_client()

@pytest.fixture(scope='session')
def init_database():
    """Initialize the test database."""
    # Connect to default 'postgres' db to create/drop test db if needed
    # But we assume 'smart_ecommerce_test_db' exists from setup step.
    
    # Read schema
    with open('database_schema.sql', 'r') as f:
        schema_sql = f.read()
    
    # Close any existing connections from app import
    close_all_connections()
    
    # Connect to test DB and apply schema
    conn = psycopg2.connect(
        host=test_config.DB_HOST,
        port=test_config.DB_PORT,
        database=test_config.DB_NAME,
        user=test_config.DB_USER,
        password=test_config.DB_PASSWORD
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Apply schema (it contains DROP TABLE statements)
    cursor.execute(schema_sql)
    
    cursor.close()
    conn.close()
    
    yield
    
    # Teardown (optional, we leave DB for inspection if needed)

@pytest.fixture(scope='function')
def db(init_database):
    """
    Provide a clean database for each test.
    This fixture runs for every test function.
    It truncates tables to ensure isolation.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Truncate all tables
    tables = [
        'payments', 'order_items', 'orders', 'cart', 'reviews', 'wishlists',
        'products', 'categories', 'users', 'admin'
    ]
    
    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
    
    conn.commit()
    cursor.close()
    # Return connection if needed, but usually we use models
    yield conn
    
    # Connection is released/closed by model calls or teardown
