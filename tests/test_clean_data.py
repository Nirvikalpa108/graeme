import sys
import os
import pandas as pd
sys.path.append(os.path.abspath("src"))
from clean_data import clean_raw_csv

def test_clean_data_renames_columns(tmp_path):
    raw_path = "data/myntra_products_catalog.csv"
    cleaned_df = clean_raw_csv(raw_path)

    expected_columns = [
        "product_id",
        "product_name",
        "product_brand",
        "gender",
        "price_inr",
        "description",
        "primary_color"
    ]

    assert all(col in cleaned_df.columns for col in expected_columns), "Not all expected columns found"
    assert cleaned_df.shape[0] > 0, "No data rows found"

    # Save cleaned file to temp dir
    cleaned_path = tmp_path / "cleaned_styles.csv"
    cleaned_df.to_csv(cleaned_path, index=False)

    assert os.path.exists(cleaned_path), "Cleaned CSV was not saved"
