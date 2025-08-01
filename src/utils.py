import os
import psycopg2
from contextlib import contextmanager
from dotenv import load_dotenv

# Load env variables
load_dotenv(dotenv_path=".env")

@contextmanager
def db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT"))
    )
    try:
        yield conn
    finally:
        conn.close()
