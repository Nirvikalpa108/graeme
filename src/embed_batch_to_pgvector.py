import time
from psycopg2.extras import execute_batch
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer
from utils import db_connection

print("🚀 Starting full DB embedding...")
start_time = time.time()

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

with db_connection() as conn:
    register_vector(conn)
    with conn.cursor() as cursor:
        # Fetch products with descriptions
        cursor.execute("SELECT product_id, description FROM products WHERE description IS NOT NULL;")
        rows = cursor.fetchall()
        print(f"📦 Fetched {len(rows)} rows")

        # Extract data
        product_ids = [row[0] for row in rows]
        descriptions = [row[1] for row in rows]

        print("🧠 Generating embeddings...")
        embeddings = model.encode(descriptions, batch_size=64, show_progress_bar=True)

        # Batch insert embeddings using pgvector native support
        data = list(zip(product_ids, embeddings))  # embeddings are numpy arrays

        print("💾 Inserting into product_embeddings...")
        execute_batch(cursor, """
            INSERT INTO product_embeddings (product_id, embedding)
            VALUES (%s, %s)
            ON CONFLICT (product_id) DO UPDATE SET embedding = EXCLUDED.embedding;
        """, data)

    conn.commit()

elapsed_time = time.time() - start_time
print(f"✅ Done embedding all products. ⏱️ Took {elapsed_time:.2f} seconds.")
