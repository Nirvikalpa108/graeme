import os
import time
import psycopg2
from psycopg2.extras import execute_batch
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
cursor = conn.cursor()

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Fetch all products
cursor.execute("SELECT product_id, description FROM products WHERE description IS NOT NULL;")
rows = cursor.fetchall()
print(f"📦 Fetched {len(rows)} rows")

# Batch encode descriptions
product_ids = [row[0] for row in rows]
descriptions = [row[1] for row in rows]

print("🧠 Generating embeddings...")
embeddings = model.encode(descriptions, batch_size=64, show_progress_bar=True)

# Prepare data for batch insert
data = [(pid, embedding.tolist()) for pid, embedding in zip(product_ids, embeddings)]

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
