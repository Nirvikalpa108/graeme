import os
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import numpy as np

# Load env
#load_dotenv(dotenv_path=".env.local", override=True)
load_dotenv(dotenv_path=".env")

# Init model
model = SentenceTransformer("all-MiniLM-L6-v2")

print("🚀 Embedding one product into pgvector...")

# Connect to DB
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT"))
)
cur = conn.cursor()

# Fetch one row
cur.execute("SELECT product_id, description FROM products LIMIT 1;")
row = cur.fetchone()
product_id, description = row
print(f"🛍️  Product ID: {product_id}")
print(f"📝 Description: {description[:60]}...")

# Generate embedding
embedding = model.encode(description)
embedding_list = embedding.tolist()

# Insert into pgvector table
cur.execute("""
    INSERT INTO product_embeddings (product_id, embedding)
    VALUES (%s, %s)
    ON CONFLICT (product_id) DO UPDATE SET embedding = EXCLUDED.embedding;
""", (product_id, embedding_list))

conn.commit()
cur.close()
conn.close()
print("✅ Done. Row inserted into product_embeddings.")
