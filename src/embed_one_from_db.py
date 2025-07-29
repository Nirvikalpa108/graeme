import os
import psycopg2
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load env vars
load_dotenv(dotenv_path=".env")

print("🚀 Starting embedding from DB...")

# Connect to Postgres
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT"))
)
cursor = conn.cursor()

# Fetch first row
cursor.execute("SELECT product_id, description FROM products LIMIT 1;")
row = cursor.fetchone()
product_id, description = row
print(f"🛍️  Product ID: {product_id}")
print(f"📝 Description: {description[:80]}...")

# Embed description
model = SentenceTransformer("all-MiniLM-L6-v2")
embedding = model.encode(description)

print("🧠 Embedding vector (first 10 dims):", embedding[:10])
print("✅ Embedding complete.")

cursor.close()
conn.close()
