import pandas as pd

def clean_raw_csv(input_path: str) -> pd.DataFrame:
    df = pd.read_csv(input_path)

    # Rename columns to be SQL-safe
    df = df.rename(columns={
        'ProductID': 'product_id',
        'ProductName': 'product_name',
        'ProductBrand': 'product_brand',
        'Gender': 'gender',
        'Price (INR)': 'price_inr',
        'NumImages': 'num_images',
        'Description': 'description',
        'PrimaryColor': 'primary_color'
    })

    return df
