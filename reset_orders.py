from database.db_connection import execute_query

def reset_orders():
    query = "UPDATE orders SET order_status = 'Confirmed', updated_at = CURRENT_TIMESTAMP WHERE order_status = 'Delivered'"
    result = execute_query(query, commit=True)
    print(f"Updated {result} orders back to 'Confirmed' status.")

if __name__ == "__main__":
    reset_orders()
