from database.db_connection import execute_dict_query
import logging

logging.basicConfig(level=logging.INFO)

def check_payments():
    # Check if there are any failed payments blocking new ones
    res = execute_dict_query("SELECT id, order_id, payment_status FROM payments", fetch_all=True)
    print(f"Current Payments: {res}")
    
    # Check orders without payments
    query = """
        SELECT o.id, o.order_number, o.order_status, p.id as payment_id
        FROM orders o
        LEFT JOIN payments p ON o.id = p.order_id
        WHERE p.id IS NULL
    """
    res = execute_dict_query(query, fetch_all=True)
    print(f"Orders without payment records: {res}")

if __name__ == "__main__":
    check_payments()
