import os
import psycopg2
import pytest
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector
import numpy as np
from sentence_transformers import SentenceTransformer

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
    register_vector(db_connection)
    with db_connection.cursor() as cur:
        cur.execute("SELECT embedding FROM product_embeddings LIMIT 5;")
        rows = cur.fetchall()
        for idx, row in enumerate(rows):
            vec = row[0]
            assert isinstance(vec, np.ndarray)
            assert len(vec) == 384, f"Row {idx} has incorrect vector length: {len(vec)}"

def test_generate_embedding_from_db_description(db_connection):
    with db_connection.cursor() as cur:
        cur.execute("SELECT product_id, description FROM products LIMIT 1;")
        row = cur.fetchone()
        assert row is not None, "No row returned from database"

        product_id, description = row
        assert description is not None and len(description) > 0, "Description is empty"

        model = SentenceTransformer("all-MiniLM-L6-v2")
        embedding = model.encode(description)

        assert isinstance(embedding, np.ndarray), "Embedding is not a NumPy array"
        assert embedding.shape[0] == 384, f"Expected embedding of size 384, got {embedding.shape[0]}"
        assert np.any(embedding != 0), "Embedding is all zeros"
        assert np.all(np.isfinite(embedding)), "Embedding contains NaN or Inf"

def test_cosine_similarity_of_stored_embedding(db_connection):
    register_vector(db_connection)

    product_id = 10017413
    description = (
        "Black and grey printed medium trolley bag, secured with a TSA lock"
        "One handle on the top and one on the side, has a trolley with a retractable handle on the top and four corner mounted inline skate wheels"
        "One main zip compartment, zip lining, two compression straps with click clasps, one zip compartment on the flap with three zip pockets"
        "Warranty: 5 yearsWarranty provided by Brand Owner / Manufacturer"
    )

    model = SentenceTransformer("all-MiniLM-L6-v2")
    expected_embedding = model.encode(description)

    with db_connection.cursor() as cur:
        cur.execute("SELECT embedding FROM product_embeddings WHERE product_id = %s;", (product_id,))
        row = cur.fetchone()

    assert row is not None, f"No embedding found for product_id {product_id}"
    actual_embedding = row[0]  

    # Cosine similarity calculation
    cosine_similarity = np.dot(expected_embedding, actual_embedding) / (
        np.linalg.norm(expected_embedding) * np.linalg.norm(actual_embedding)
    )

    # Threshold for similarity check
    assert cosine_similarity > 0.99, (
        f"Embedding mismatch for product {product_id}\n"
        f"Cosine similarity = {cosine_similarity:.6f}\n"
        f"Expected[:5] = {expected_embedding[:5]}\n"
        f"Actual[:5]   = {actual_embedding[:5]}"
    )

    print(f"✅ Cosine similarity test passed. Similarity = {cosine_similarity:.6f}")
