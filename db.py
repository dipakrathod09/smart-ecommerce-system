import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="smart_ecommerce_db",
        user="postgres",
        password="Admin@123"
    )
