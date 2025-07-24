import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extensions import register_adapter, AsIs
from clean_data import clean_raw_csv
import os
import time

register_adapter(np.int64, AsIs)
register_adapter(np.int32, AsIs)

# Delay to wait for db to be ready
time.sleep(5)

# DB connection params from environment variables
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=5432
)
cursor = conn.cursor()

df = clean_raw_csv("data/myntra_products_catalog.csv")

for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO products (product_id, product_name, product_brand, gender, price_inr, description, primary_color)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (product_id) DO NOTHING;
    """, (
        int(row.product_id),
        row.product_name,
        row.product_brand,
        row.gender,
        int(row.price_inr),
        row.description,
        row.primary_color
    ))

conn.commit()
cursor.close()
conn.close()
