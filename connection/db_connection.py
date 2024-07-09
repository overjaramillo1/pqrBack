import os
import pg8000


DB_ENDPOINT = os.environ['DB_ENDPOINT']
DB_USERNAME = os.environ['DB_USERNAME']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_DATABASE = os.environ['DB_DATABASE']

def connect_to_database():
    try:
        conn = pg8000.connect(
        host=DB_ENDPOINT,
        database=DB_DATABASE,
        user=DB_USERNAME,
        password=DB_PASSWORD)
        return conn
    except Exception as e:
        print(str(e))
        return None