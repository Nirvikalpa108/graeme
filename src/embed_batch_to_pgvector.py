import os
import time
import psycopg2
from psycopg2.extras import execute_batch
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

print("🚀 Starting full DB embedding...")
start_time = time.time()

# Load env variables
load_dotenv(dotenv_path=".env")

# DB connection
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT"))
)

# ✅ Register pgvector adapter
register_vector(conn)
cursor = conn.cursor()

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

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
cursor.close()
conn.close()

elapsed_time = time.time() - start_time
print(f"✅ Done embedding all products. ⏱️ Took {elapsed_time:.2f} seconds.")
