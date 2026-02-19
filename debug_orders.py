from database.db_connection import execute_dict_query

def debug_orders():
    query = "SELECT id, order_number, order_status, updated_at FROM orders"
    orders = execute_dict_query(query, fetch_all=True)
    if orders:
        print("Existing Orders:")
        for o in orders:
            print(f"ID: {o['id']}, Number: {o['order_number']}, Status: {o['order_status']}, Updated: {o['updated_at']}")
    else:
        print("No orders found.")

if __name__ == "__main__":
    debug_orders()
