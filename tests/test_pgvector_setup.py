import os
import psycopg2
import pytest
from dotenv import load_dotenv

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

def test_pgvector_extension_installed(db_connection):
    with db_connection.cursor() as cur:
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        result = cur.fetchone()
        assert result is not None, "pgvector extension is not installed"

def test_embedding_table_exists(db_connection):
    with db_connection.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'product_embeddings'
            );
        """)
        exists = cur.fetchone()[0]
        assert exists, "Table 'product_embeddings' does not exist"

def test_all_products_embedded(db_connection):
    with db_connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM products WHERE description IS NOT NULL;")
        expected_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM product_embeddings;")
        actual_count = cur.fetchone()[0]
        assert expected_count == actual_count, f"{expected_count} products with descriptions, but {actual_count} embeddings"

def test_no_null_embeddings(db_connection):
    with db_connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM product_embeddings WHERE embedding IS NULL;")
        null_count = cur.fetchone()[0]
        assert null_count == 0, f"Found {null_count} null embeddings"

def test_embedding_vector_dimensions(db_connection):
    with db_connection.cursor() as cur:
        cur.execute("SELECT embedding FROM product_embeddings LIMIT 5;")
        rows = cur.fetchall()
        for idx, row in enumerate(rows):
            vec = row[0]
            assert len(vec) == 384, f"Row {idx} has incorrect vector length: {len(vec)}"