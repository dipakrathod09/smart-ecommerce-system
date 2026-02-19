
from database.db_connection import execute_dict_query
from datetime import datetime

def check_returnable():
    query = """
        SELECT id, order_number, order_status, updated_at,
               (order_status = 'Delivered' AND updated_at >= CURRENT_TIMESTAMP - INTERVAL '7 days') as is_returnable
        FROM orders
    """
    results = execute_dict_query(query, fetch_all=True)
    print(f"{'ID':<5} {'Order #':<20} {'Status':<15} {'Returnable':<10} {'Updated At'}")
    print("-" * 70)
    for r in results:
        print(f"{r['id']:<5} {r['order_number']:<20} {r['order_status']:<15} {str(r['is_returnable']):<10} {r['updated_at']}")

if __name__ == "__main__":
    check_returnable()
