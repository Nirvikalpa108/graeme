import pytest
from utils import db_connection 

@pytest.fixture(scope="module")
def db_cursor():
    with db_connection() as conn:
        with conn.cursor() as cur:
            yield cur

def test_row_count(db_cursor):
    cur = db_cursor
    cur.execute("SELECT COUNT(*) FROM products;")  # replace 'products' with your table name
    count = cur.fetchone()[0]
    print(f"Row count: {count}")
    assert count > 0, "Table 'products' should contain at least one row"

def test_product_id_uniqueness(db_cursor):
    cur = db_cursor
    cur.execute("SELECT COUNT(DISTINCT product_id), COUNT(*) FROM products;")
    unique, total = cur.fetchone()
    assert unique == total, f"Found duplicate ProductIDs: {total - unique}"

def test_expected_columns_exist(db_cursor):
    cur = db_cursor
    cur.execute("SELECT * FROM products LIMIT 1;")
    colnames = [desc[0] for desc in cur.description]
    expected = {
        "product_id", "product_name", "product_brand",
        "gender", "price_inr", "num_images",
        "description", "primary_color"
    }
    assert expected.issubset(set(colnames)), f"Missing columns: {expected - set(colnames)}"

def test_price_is_non_negative(db_cursor):
    cur = db_cursor
    cur.execute("SELECT COUNT(*) FROM products WHERE price_inr < 0;")
    count = cur.fetchone()[0]
    assert count == 0, f"Found {count} products with negative price"

