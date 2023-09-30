import psycopg2

def get_db_connection():
    con = psycopg2.connect(
                database="smart_trading",
                user="postgres",
                password="123456",
                host="127.0.0.1",
                port="5432"
            )
    return con

