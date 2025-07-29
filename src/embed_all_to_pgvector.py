import os
import psycopg2
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load env vars
load_dotenv(dotenv_path=".env")

print("🚀 Starting batch embedding...")

# Connect to DB
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

# Get all products with descriptions
cursor.execute("SELECT product_id, description FROM products WHERE description IS NOT NULL;")
rows = cursor.fetchall()

for product_id, description in rows:
    embedding = model.encode(description).tolist()
    cursor.execute("""
        INSERT INTO product_embeddings (product_id, embedding)
        VALUES (%s, %s)
        ON CONFLICT (product_id) DO UPDATE SET embedding = EXCLUDED.embedding;
    """, (product_id, embedding))

conn.commit()
cursor.close()
conn.close()
print(f"✅ Embedded {len(rows)} products.")
