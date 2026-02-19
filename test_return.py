from database.db_connection import execute_query

def mark_as_delivered(order_id):
    query = "UPDATE orders SET order_status = 'Delivered', updated_at = CURRENT_TIMESTAMP WHERE id = %s"
    result = execute_query(query, (order_id,), commit=True)
    if result:
        print(f"Order {order_id} marked as 'Delivered'.")
    else:
        print(f"Failed to update order {order_id}.")

if __name__ == "__main__":
    mark_as_delivered(9)
