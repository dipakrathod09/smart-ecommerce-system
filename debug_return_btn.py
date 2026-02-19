from database.db_connection import execute_dict_query

def debug_return_logic():
    query = "SELECT id, order_number, order_status, updated_at FROM orders"
    orders = execute_dict_query(query, fetch_all=True)
    for o in orders:
        status_match = o['order_status'] == 'Delivered'
        print(f"ID:{o['id']} STATUS:{o['order_status']} MATCH:{status_match} TIME:{o['updated_at']}")

if __name__ == "__main__":
    debug_return_logic()
