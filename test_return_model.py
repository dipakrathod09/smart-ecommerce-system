from models.order import Order
import logging

# Mock session for logging if needed
logging.basicConfig(level=logging.INFO)

def test_return():
    order_id = 9
    reason = "Test Reason from Script"
    success = Order.return_order(order_id, reason)
    print(f"Return status: {success}")
    
    from database.db_connection import execute_dict_query
    res = execute_dict_query("SELECT id, order_status, return_reason FROM orders WHERE id=%s", (order_id,), fetch_one=True)
    print(f"Updated Order: {res}")

if __name__ == "__main__":
    test_return()
