from database.db_connection import execute_dict_query

def check_columns():
    query = "SELECT * FROM orders LIMIT 1"
    columns_info = ""
    try:
        result = execute_dict_query(query, fetch_one=True)
        if result:
            columns_info += f"Orders: {list(result.keys())}\n"
        else:
            schema_query = "SELECT column_name FROM information_schema.columns WHERE table_name = 'orders'"
            columns = execute_dict_query(schema_query, fetch_all=True)
            cols = [c['column_name'] for c in columns]
            columns_info += f"Orders: {cols}\n"
            
        schema_query = "SELECT column_name FROM information_schema.columns WHERE table_name = 'payments'"
        columns = execute_dict_query(schema_query, fetch_all=True)
        cols = [c['column_name'] for c in columns]
        columns_info += f"Payments: {cols}\n"
        
        with open("schema_output.txt", "w") as f:
            f.write(columns_info)
        print("Schema info written to schema_output.txt")
    except Exception as e:
        print(f"Error checking columns: {str(e)}")

if __name__ == "__main__":
    check_columns()
