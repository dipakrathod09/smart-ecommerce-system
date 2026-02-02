"""
Database Connection Module
Handles PostgreSQL database connections with connection pooling
"""

import psycopg2
from psycopg2 import pool
from psycopg2 import extras
from config import get_config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global connection pool
connection_pool = None


def initialize_connection_pool():
    """
    Initialize PostgreSQL connection pool
    This should be called when the application starts
    """
    global connection_pool
    
    if connection_pool is None:
        try:
            config = get_config()
            
            # Create connection pool
            connection_pool = psycopg2.pool.SimpleConnectionPool(
                config.DB_MIN_CONN,
                config.DB_MAX_CONN,
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD
            )
            
            if connection_pool:
                logger.info("Connection pool created successfully")
                return True
            else:
                logger.error("Failed to create connection pool")
                return False
                
        except Exception as e:
            logger.error(f"Error creating connection pool: {str(e)}")
            return False
    
    return True


def get_db_connection():
    """
    Get a connection from the pool
    
    Returns:
        connection: PostgreSQL connection object
        
    Usage:
        conn = get_db_connection()
        cursor = conn.cursor()
        # ... execute queries ...
        cursor.close()
        release_db_connection(conn)
    """
    global connection_pool
    
    try:
        # Initialize pool if not already done
        if connection_pool is None:
            initialize_connection_pool()
        
        # Get connection from pool
        if connection_pool:
            connection = connection_pool.getconn()
            if connection:
                return connection
            else:
                logger.error("Failed to get connection from pool")
                return None
        else:
            logger.error("Connection pool is None")
            return None
            
    except Exception as e:
        logger.error(f"Error getting connection: {str(e)}")
        return None


def release_db_connection(connection):
    """
    Return a connection back to the pool
    
    Args:
        connection: PostgreSQL connection object to release
    """
    global connection_pool
    
    try:
        if connection_pool and connection:
            connection_pool.putconn(connection)
            
    except Exception as e:
        logger.error(f"Error releasing connection: {str(e)}")


def close_all_connections():
    """
    Close all connections in the pool
    This should be called when the application shuts down
    """
    global connection_pool
    
    try:
        if connection_pool:
            connection_pool.closeall()
            logger.info("All database connections closed")
            connection_pool = None
            
    except Exception as e:
        logger.error(f"Error closing connections: {str(e)}")


def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """
    Execute a database query with automatic connection management
    
    Args:
        query (str): SQL query to execute
        params (tuple): Query parameters (for parameterized queries)
        fetch_one (bool): If True, return single row
        fetch_all (bool): If True, return all rows
        commit (bool): If True, commit the transaction (for INSERT/UPDATE/DELETE)
    
    Returns:
        Result based on fetch parameters, or None
        
    Usage:
        # Fetch all rows
        users = execute_query("SELECT * FROM users", fetch_all=True)
        
        # Fetch one row
        user = execute_query("SELECT * FROM users WHERE id = %s", (1,), fetch_one=True)
        
        # Insert/Update/Delete
        execute_query("INSERT INTO users (name) VALUES (%s)", ("John",), commit=True)
    """
    conn = None
    cursor = None
    result = None
    
    try:
        # Get connection
        conn = get_db_connection()
        if not conn:
            logger.error("Failed to get database connection")
            return None
        
        # Create cursor
        cursor = conn.cursor()
        
        # Execute query
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Fetch results if requested
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        
        # Commit if requested (for INSERT/UPDATE/DELETE)
        if commit:
            conn.commit()
            result = cursor.rowcount  # Return number of affected rows
        
        return result
        
    except Exception as e:
        logger.error(f"Database query error: {str(e)}")
        if conn:
            conn.rollback()  # Rollback on error
        return None
        
    finally:
        # Clean up
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


def execute_dict_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    Execute query and return results as dictionary
    Useful when you want column names with values
    
    Args:
        query (str): SQL query to execute
        params (tuple): Query parameters
        fetch_one (bool): Return single dict
        fetch_all (bool): Return list of dicts
    
    Returns:
        Dictionary or list of dictionaries with column names as keys
        
    Usage:
        user = execute_dict_query("SELECT * FROM users WHERE id = %s", (1,), fetch_one=True)
        # Returns: {'id': 1, 'name': 'John', 'email': 'john@example.com'}
    """
    conn = None
    cursor = None
    result = None
    
    try:
        conn = get_db_connection()
        if not conn:
            return None
        
        # Use DictCursor for dictionary results
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Check if this is an INSERT/UPDATE/DELETE with RETURNING
        query_upper = query.strip().upper()
        needs_commit = any(query_upper.startswith(cmd) for cmd in ['INSERT', 'UPDATE', 'DELETE'])
        
        if fetch_one:
            row = cursor.fetchone()
            result = dict(row) if row else None
        elif fetch_all:
            rows = cursor.fetchall()
            result = [dict(row) for row in rows] if rows else []
        
        # Commit if it's a write operation
        if needs_commit:
            conn.commit()
        
        return result
        
    except Exception as e:
        logger.error(f"Database dict query error: {str(e)}")
        if conn:
            conn.rollback()  # Rollback on error
        return None
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


def test_connection():
    """
    Test database connection
    Returns True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            release_db_connection(conn)
            logger.info("Database connection test successful")
            return True
        else:
            logger.error("Database connection test failed")
            return False
            
    except Exception as e:
        logger.error(f"Database connection test error: {str(e)}")
        return False


# Initialize connection pool when module is imported
initialize_connection_pool()