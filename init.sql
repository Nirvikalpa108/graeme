CREATE TABLE products (
    product_id     INTEGER PRIMARY KEY,
    product_name   TEXT NOT NULL,
    product_brand  TEXT,
    gender         TEXT,
    price_inr      INTEGER,
    num_images     INTEGER, 
    description    TEXT,
    primary_color  TEXT
);
