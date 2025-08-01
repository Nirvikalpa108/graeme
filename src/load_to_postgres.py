import numpy as np
from psycopg2.extensions import register_adapter, AsIs
from clean_data import clean_raw_csv
import time
from utils import db_connection 

# Register numpy int types so psycopg2 can handle them
register_adapter(np.int64, AsIs)
register_adapter(np.int32, AsIs)

# Delay to wait for db to be ready
time.sleep(5)

df = clean_raw_csv("data/myntra_products_catalog.csv")
print(f"✅ Loaded CSV with {len(df)} rows")

with db_connection() as conn:
    with conn.cursor() as cursor:
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO products (
                    product_id, product_name, product_brand,
                    gender, price_inr, num_images, description, primary_color
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (product_id) DO NOTHING;
            """, (
                int(row.product_id),
                row.product_name,
                row.product_brand,
                row.gender,
                int(row.price_inr),
                int(row.num_images),
                row.description,
                row.primary_color
            ))
        conn.commit()
print("✅ Finished inserting rows into Postgres")
