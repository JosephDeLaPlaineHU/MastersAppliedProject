import psycopg2
import sys

try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        database="masters_project",
        user="postgres",
        password="123456",
        port="5433"
    )
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
