import pytest
from models.user import User
from models.product import Product
from models.order import Order
from models.cart import Cart
from services.order_service import OrderService
from services.product_service import ProductService

# ===================================================================
# USER MODEL TESTS
# ===================================================================

def test_create_user(db):
    """Test user creation"""
    user = User.create(
        full_name="Test User",
        email="test@example.com",
        password_hash="hashed_secret",
        phone="1234567890"
    )
    assert user is not None
    assert user['email'] == "test@example.com"
    assert user['id'] is not None

def test_get_user_by_email(db):
    """Test fetching user by email"""
    User.create("Test User", "test@example.com", "hash", "1234567890")
    user = User.get_user_with_credentials("test@example.com")
    assert user is not None
    assert user['full_name'] == "Test User"

def test_email_exists(db):
    """Test email existence check"""
    User.create("Test User", "test@example.com", "hash", "1234567890")
    assert User.email_exists("test@example.com") is True
    assert User.email_exists("nonexistent@example.com") is False

# ===================================================================
# PRODUCT MODEL TESTS
# ===================================================================

def test_create_product(db):
    """Test product creation"""
    # Need a category first
    from database.db_connection import execute_query
    execute_query("INSERT INTO categories (name) VALUES ('Test Cat')", commit=True)
    # Use tuple index 0 or execute_dict_query
    cat = execute_query("SELECT id FROM categories WHERE name='Test Cat'", fetch_one=True)
    
    product = Product.create(
        category_id=cat[0],
        name='Test Product',
        description='Desc',
        price=100.0,
        stock=10,
        brand='Brand'
    )
    assert product is not None
    assert product['name'] == 'Test Product'
    assert product['stock'] == 10

def test_product_stock_update(db):
    """Test stock update"""
    # Setup category and product
    from database.db_connection import execute_query
    execute_query("INSERT INTO categories (name) VALUES ('Test Cat')", commit=True)
    cat = execute_query("SELECT id FROM categories WHERE name='Test Cat'", fetch_one=True)
    product = Product.create(
        category_id=cat[0], 
        name='P1',
        description='Desc',
        price=10, 
        stock=10
    )
    
    # Decrease stock
    Product.update_stock(product['id'], -5)
    updated = Product.get_by_id(product['id'])
    assert updated['stock'] == 5
    
    # Increase stock
    Product.update_stock(product['id'], 2)
    updated = Product.get_by_id(product['id'])
    assert updated['stock'] == 7

# ===================================================================
# ORDER SERVICE & MODEL TESTS (Lifecycle)
# ===================================================================

def test_order_lifecycle(db):
    """
    Test complete order lifecycle:
    Cart -> Create Order -> Stock Decrease (Trigger) -> Finalize -> Cancel -> Stock Restore
    """
    # 1. Setup Data
    from database.db_connection import execute_query
    execute_query("INSERT INTO categories (name) VALUES ('Test Cat')", commit=True)
    cat = execute_query("SELECT id FROM categories WHERE name='Test Cat'", fetch_one=True)
    
    # Create User
    user = User.create("Buyer", "buyer@example.com", "hash")
    
    # Create Product with stock = 10
    product = Product.create(
        category_id=cat[0], 
        name='Phone', 
        description='Desc',
        price=1000, 
        stock=10
    )
    
    # 2. Add to Cart
    Cart.add_item(user['id'], product['id'], 2)
    cart_items = Cart.get_cart_items(user['id'])
    assert len(cart_items) == 1
    assert cart_items[0]['quantity'] == 2
    
    # 3. Create Order via Service
    shipping_data = {
        'address': '123 St',
        'city': 'City',
        'state': 'State',
        'pincode': '123456',
        'phone': '9999999999'
    }
    order = OrderService.create_order(user['id'], shipping_data)
    assert order is not None
    assert order['order_number'] is not None
    
    # 4. Verify Stock DECREASED (Trigger check)
    p_after_order = Product.get_by_id(product['id'])
    assert p_after_order['stock'] == 8 # 10 - 2
    
    # 5. Finalize Order (Stock should NOT decrease further)
    success = OrderService.finalize_order(order['id'])
    assert success is True
    
    p_after_finalize = Product.get_by_id(product['id'])
    assert p_after_finalize['stock'] == 8 # Still 8
    
    # Verify status
    o_updated = OrderService.get_order_by_id(order['id'])
    assert o_updated['order_status'] == 'Confirmed'

    # 6. Cancel Order (Stock should RESTORE)
    success, msg = OrderService.cancel_order(order['id'], user['id'], "Changed mind")
    assert success is True
    
    p_after_cancel = Product.get_by_id(product['id'])
    assert p_after_cancel['stock'] == 10 # Restored to 10
    
    o_cancelled = OrderService.get_order_by_id(order['id'])
    assert o_cancelled['order_status'] == 'Cancelled'

def test_insufficient_stock(db):
    """Test order creation fails if stock is low"""
    # Setup
    from database.db_connection import execute_query
    execute_query("INSERT INTO categories (name) VALUES ('Test Cat')", commit=True)
    cat = execute_query("SELECT id FROM categories WHERE name='Test Cat'", fetch_one=True)
    user = User.create("Buyer", "buyer@example.com", "hash")
    product = Product.create(
        category_id=cat[0], name='Rare', description='Desc', price=10, stock=1
    )
    
    # Add 2 to cart (allowed in cart, but failing at checkout?)
    # Cart.add_item checks stock, so we simulate bypass or concurrent change
    # Actually Cart.add_item calls Product.check_stock.
    # So we force add using raw SQL to simulate "added when stock was 2, now 1"
    execute_query(
        "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
        (user['id'], product['id'], 2),
        commit=True
    )
    
    # Try creating order
    shipping_data = {'address': 'Addr', 'city': 'C', 'state': 'S', 'pincode': '1', 'phone': '1'}
    order = OrderService.create_order(user['id'], shipping_data)
    
    assert order is None # Should fail due to insufficient stock check in Service

# ===================================================================
# CART MODEL TESTS
# ===================================================================

def test_cart_operations(db):
    """Test cart add, update, remove, clear"""
    # Setup
    from database.db_connection import execute_query
    execute_query("INSERT INTO categories (name) VALUES ('Test Cat')", commit=True)
    cat = execute_query("SELECT id FROM categories WHERE name='Test Cat'", fetch_one=True)
    user = User.create("Buyer", "cart@example.com", "hash")
    product = Product.create(
        category_id=cat[0], name='Item', description='Desc', price=10, stock=100
    )
    
    # Add
    assert Cart.add_item(user['id'], product['id'], 1) is True
    count = Cart.get_cart_count(user['id'])
    assert count == 1
    
    # Update
    items = Cart.get_cart_items(user['id'])
    cart_id = items[0]['cart_id']
    assert Cart.update_quantity(cart_id, 5) is True
    items = Cart.get_cart_items(user['id'])
    assert items[0]['quantity'] == 5
    
    # Remove
    assert Cart.remove_item(cart_id) is True
    count = Cart.get_cart_count(user['id'])
    assert count == 0
    
    # Clear
    Cart.add_item(user['id'], product['id'], 1)
    assert Cart.clear_cart(user['id']) is True
    count = Cart.get_cart_count(user['id'])
    assert count == 0
