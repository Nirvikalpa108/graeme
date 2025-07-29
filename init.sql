-- Main product data table
CREATE TABLE IF NOT EXISTS products (
    product_id     INTEGER PRIMARY KEY,
    product_name   TEXT NOT NULL,
    product_brand  TEXT,
    gender         TEXT,
    price_inr      INTEGER,
    num_images     INTEGER, 
    description    TEXT,
    primary_color  TEXT
);

-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Embeddings table using pgvector
CREATE TABLE IF NOT EXISTS product_embeddings (
    product_id INTEGER PRIMARY KEY REFERENCES products(product_id), -- adds a foreign key constraint to link embeddings back to products
    embedding vector(384)
);
