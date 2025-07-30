import os
import pytest
import psycopg2
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Load env vars for Docker-local and fallback
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
