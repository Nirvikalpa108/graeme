import os
import psycopg2
from contextlib import contextmanager
from dotenv import load_dotenv

# Load env variables
load_dotenv(dotenv_path=".env")

@contextmanager
def db_connection():
    conn_kwargs = dict(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT"))
    )
    if sslmode := os.getenv("DB_SSLMODE"):
        conn_kwargs["sslmode"] = sslmode
    conn = psycopg2.connect(**conn_kwargs)
    try:
        yield conn
    finally:
        conn.close()
