"""
Create Admin and Test User Script
Run this to create properly hashed admin and test user accounts
"""

import bcrypt
import psycopg2

# Database configuration - UPDATE THESE!
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'smart_ecommerce_db',
    'user': 'postgres',
    'password': 'Admin@123'  # ⚠️ UPDATE THIS!
}

def create_admin():
    """Create admin account with properly hashed password"""
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Password to hash
        password = "admin123"
        
        # Hash password with bcrypt
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        password_hash_str = password_hash.decode('utf-8')
        
        print(f"Password: {password}")
        print(f"Hash: {password_hash_str}")
        print()
        
        # Delete existing admin if any
        cursor.execute("DELETE FROM admin WHERE username = 'admin'")
        conn.commit()
        print("✓ Cleared existing admin account")
        
        # Insert admin with hashed password
        cursor.execute("""
            INSERT INTO admin (username, password_hash, email, full_name, is_super_admin)
            VALUES (%s, %s, %s, %s, %s)
        """, ('admin', password_hash_str, 'admin@example.com', 'System Administrator', True))
        
        conn.commit()
        print("✓ Admin account created successfully!")
        print()
        print("Admin Login Credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print()
        
        # Verify the account was created
        cursor.execute("SELECT username, email, is_super_admin FROM admin WHERE username = 'admin'")
        result = cursor.fetchone()
        if result:
            print(f"✓ Verification: Admin account exists - {result}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error creating admin: {str(e)}")
        return False


def create_test_user():
    """Create test user account with properly hashed password"""
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Password to hash
        password = "password123"
        
        # Hash password with bcrypt
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        password_hash_str = password_hash.decode('utf-8')
        
        # Check if user already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = 'test@example.com'")
        if cursor.fetchone()[0] > 0:
            print("✓ Test user already exists")
            cursor.close()
            conn.close()
            return True
        
        # Insert test user with hashed password
        cursor.execute("""
            INSERT INTO users (full_name, email, password_hash, phone, is_active)
            VALUES (%s, %s, %s, %s, %s)
        """, ('Test User', 'test@example.com', password_hash_str, '1234567890', True))
        
        conn.commit()
        print("✓ Test user created successfully!")
        print()
        print("Test User Login Credentials:")
        print("  Email: test@example.com")
        print("  Password: password123")
        print()
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error creating test user: {str(e)}")
        return False


def test_login():
    """Test if the login would work"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Test admin login
        print("\nTesting Admin Login...")
        cursor.execute("SELECT username, password_hash FROM admin WHERE username = 'admin'")
        admin = cursor.fetchone()
        
        if admin:
            username, stored_hash = admin
            test_password = "admin123"
            
            # Verify password
            if bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8')):
                print("✓ Admin password verification SUCCESSFUL!")
            else:
                print("✗ Admin password verification FAILED!")
        else:
            print("✗ Admin account not found!")
        
        # Test user login
        print("\nTesting User Login...")
        cursor.execute("SELECT email, password_hash FROM users WHERE email = 'test@example.com'")
        user = cursor.fetchone()
        
        if user:
            email, stored_hash = user
            test_password = "password123"
            
            # Verify password
            if bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8')):
                print("✓ User password verification SUCCESSFUL!")
            else:
                print("✗ User password verification FAILED!")
        else:
            print("✓ User account not yet created (run create_test_user)")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error testing login: {str(e)}")


def check_database():
    """Check if database and tables exist"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Checking database tables...")
        
        # Check tables
        tables = ['users', 'admin', 'categories', 'products', 'cart', 'orders', 'order_items', 'payments']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  ✓ {table}: {count} rows")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Database check failed: {str(e)}")
        print("\nMake sure to:")
        print("1. PostgreSQL is running")
        print("2. Database 'smart_ecommerce_db' exists")
        print("3. Schema has been loaded (run database_schema.sql)")
        print("4. Update DB_CONFIG in this script with correct password")
        return False


if __name__ == '__main__':
    print("="*70)
    print("SMART E-COMMERCE SYSTEM - CREATE ACCOUNTS SCRIPT")
    print("="*70)
    print()
    
    # Check database first
    if not check_database():
        print("\n⚠️ Database check failed! Fix database connection first.")
        exit(1)
    
    print()
    print("="*70)
    
    # Create admin
    print("\n1. Creating Admin Account...")
    print("-" * 70)
    create_admin()
    
    # Create test user
    print("\n2. Creating Test User Account...")
    print("-" * 70)
    create_test_user()
    
    # Test logins
    print("\n3. Testing Login Verification...")
    print("-" * 70)
    test_login()
    
    print()
    print("="*70)
    print("SETUP COMPLETE!")
    print("="*70)
    print()
    print("You can now login with:")
    print()
    print("ADMIN LOGIN (http://127.0.0.1:5000/auth/admin-login)")
    print("  Username: admin")
    print("  Password: admin123")
    print()
    print("USER LOGIN (http://127.0.0.1:5000/auth/login)")
    print("  Email: test@example.com")
    print("  Password: password123")
    print()
    print("="*70)
