import pytest
from models.user import User
from models.product import Product
from models.order import Order
from services.order_service import OrderService

def test_full_purchase_flow(client, db):
    """
    Test the complete flow: 
    Register -> Login -> Add to Cart -> Checkout -> Pay (COD) -> Verify
    """
    
    # ----------------------------------------------------------------
    # 1. SETUP: Create Category and Product directly in DB
    # ----------------------------------------------------------------
    from database.db_connection import execute_query
    execute_query("INSERT INTO categories (name) VALUES ('Integration Cat')", commit=True)
    cat = execute_query("SELECT id FROM categories WHERE name='Integration Cat'", fetch_one=True)
    
    # Create a product to buy using Product.create (tested in unit tests)
    # Using keyword args as fixed in unit tests
    product = Product.create(
        category_id=cat[0],
        name='Integration Product',
        description='For integration testing',
        price=500.0,
        stock=10,
        brand='TestBrand'
    )
    product_id = product['id']

    # ----------------------------------------------------------------
    # 2. REGISTER
    # ----------------------------------------------------------------
    # POST to /auth/register
    register_data = {
        'full_name': 'Integration User',
        'email': 'integration@example.com',
        'password': 'Password@123',
        'confirm_password': 'Password@123',
        'phone': '9876543210'
    }
    response = client.post('/auth/register', data=register_data, follow_redirects=True)
    
    # Perform assertions
    # Should redirect to login page or show success message
    assert response.status_code == 200
    assert b'Registration successful' in response.data or b'Login' in response.data

    # ----------------------------------------------------------------
    # 3. LOGIN
    # ----------------------------------------------------------------
    login_data = {
        'email': 'integration@example.com',
        'password': 'Password@123'
    }
    response = client.post('/auth/login', data=login_data, follow_redirects=True)
    
    # Should redirect to dashboard or home
    assert response.status_code == 200
    assert b'Welcome back' in response.data or b'Dashboard' in response.data
    
    # Verify session (via User model check or just relying on subsequent requests working)
    
    # ----------------------------------------------------------------
    # 4. ADD TO CART
    # ----------------------------------------------------------------
    # POST /cart/add/<product_id>
    response = client.post(f'/cart/add/{product_id}', data={'quantity': 1}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Product added to cart' in response.data
    
    # ----------------------------------------------------------------
    # 5. CHECKOUT
    # ----------------------------------------------------------------
    # POST /order/checkout
    shipping_data = {
        'address': '123 Integration St',
        'city': 'Test City',
        'state': 'Test State',
        'pincode': '123456',
        'phone': '9876543210'
    }
    response = client.post('/orders/checkout', data=shipping_data, follow_redirects=True)
    
    # Should redirect to payment selection
    assert response.status_code == 200
    assert b'Select Payment Method' in response.data or b'COD' in response.data
    
    # ----------------------------------------------------------------
    # 6. SELECT PAYMENT & PROCESS (COD)
    # ----------------------------------------------------------------
    # POST /payment/select-method
    response = client.post('/payment/select-method', data={'payment_method': 'COD'}, follow_redirects=True)
    
    # This should redirect to /payment/process which processes and shows success
    assert response.status_code == 200
    assert b'Payment successful' in response.data
    assert b'Payment Successful!' in response.data
    
    # ----------------------------------------------------------------
    # 7. VERIFICATION (DB STATE)
    # ----------------------------------------------------------------
    # Get the user to find their order
    user = User.get_user_with_credentials('integration@example.com')
    orders = OrderService.get_user_orders(user['id'])
    
    assert len(orders) > 0
    latest_order = orders[0]
    
    # Verify Order Status
    assert latest_order['order_status'] == 'Confirmed' # COD immediate confirm/success
    assert float(latest_order['total_amount']) == 500.0
    
    # Verify Stock Decrement
    # Initial was 10, bought 1, should be 9
    updated_product = Product.get_by_id(product_id)
    assert updated_product['stock'] == 9
    
    # Verify Cart is Empty
    from models.cart import Cart
    cart_count = Cart.get_cart_count(user['id'])
    assert cart_count == 0
