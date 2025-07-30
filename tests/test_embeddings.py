import psycopg2
import os
import pytest
from dotenv import load_dotenv
import pytest
from pgvector.psycopg2 import register_vector

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

import numpy as np

def test_pgvector_type_is_correct(db_connection):
    register_vector(db_connection)

    with db_connection.cursor() as cur:
        cur.execute("SELECT embedding FROM product_embeddings LIMIT 1;")
        row = cur.fetchone()

    assert row is not None, "No rows found in product_embeddings"
    assert isinstance(row[0], np.ndarray), f"Expected numpy.ndarray, got {type(row[0])}"
    assert row[0].shape == (384,), f"Expected vector of size 384, got shape {row[0].shape}"
