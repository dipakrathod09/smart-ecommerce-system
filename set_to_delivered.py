from database.db_connection import execute_query

def deliver_all():
    query = "UPDATE orders SET order_status = 'Delivered', updated_at = CURRENT_TIMESTAMP"
    result = execute_query(query, commit=True)
    print(f"Updated {result} orders back to 'Delivered' status.")

if __name__ == "__main__":
    deliver_all()
