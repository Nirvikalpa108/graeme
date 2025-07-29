import os
import psycopg2
import pytest
from dotenv import load_dotenv

# Load environment variables from .env
#load_dotenv(dotenv_path=".env.local", override=True)
load_dotenv(dotenv_path=".env")

@pytest.fixture(scope="module")
def db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT"))
    )
    yield conn
    conn.close()

def test_row_count(db_connection):
    with db_connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM products;")  # replace 'products' with your table name
        count = cur.fetchone()[0]
        print(f"Row count: {count}")
        assert count > 0, "Table 'products' should contain at least one row"

def test_product_id_uniqueness(db_connection):
    with db_connection.cursor() as cur:
        cur.execute("SELECT COUNT(DISTINCT product_id), COUNT(*) FROM products;")
        unique, total = cur.fetchone()
        assert unique == total, f"Found duplicate ProductIDs: {total - unique}"

def test_expected_columns_exist(db_connection):
    with db_connection.cursor() as cur:
        cur.execute("SELECT * FROM products LIMIT 1;")
        colnames = [desc[0] for desc in cur.description]
        expected = {
            "product_id", "product_name", "product_brand",
            "gender", "price_inr", "num_images",
            "description", "primary_color"
        }
        assert expected.issubset(set(colnames)), f"Missing columns: {expected - set(colnames)}"

def test_price_is_non_negative(db_connection):
    with db_connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM products WHERE price_inr < 0;")
        count = cur.fetchone()[0]
        assert count == 0, f"Found {count} products with negative price"

