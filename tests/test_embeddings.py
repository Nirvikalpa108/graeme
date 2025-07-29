from sentence_transformers import SentenceTransformer
import numpy as np
import psycopg2
import os
import pytest
from dotenv import load_dotenv

# Load environment variables
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

def test_spot_check_embedding(db_connection):
    """Spot-check that the embedding in the database is accurate for a known product."""
    product_id = 10017413
    description = "Black and grey printed medium trolley bag, secured with a TSA lock"

    model = SentenceTransformer("all-MiniLM-L6-v2")
    expected_embedding = model.encode(description)

    with db_connection.cursor() as cur:
        cur.execute("SELECT embedding FROM product_embeddings WHERE product_id = %s;", (product_id,))
        row = cur.fetchone()

    assert row is not None, f"❌ No embedding found for product_id {product_id}"
    actual_embedding = np.array(row[0])

    cosine_similarity = np.dot(expected_embedding, actual_embedding) / (
        np.linalg.norm(expected_embedding) * np.linalg.norm(actual_embedding)
    )

    if cosine_similarity <= 0.99:
        print("❌ Embedding mismatch!")
        print(f"Product ID: {product_id}")
        print(f"Description: {description}")
        print(f"Cosine Similarity: {cosine_similarity:.6f}")
        print(f"Expected (first 5 dims): {expected_embedding[:5]}")
        print(f"Actual   (first 5 dims): {actual_embedding[:5]}")

    assert cosine_similarity > 0.99, f"Embedding mismatch: cosine similarity = {cosine_similarity:.6f}"

    print(f"✅ Embedding spot check passed. Cosine similarity = {cosine_similarity:.6f}")
