from clean_data import clean_raw_csv

if __name__ == "__main__":
    df = clean_raw_csv("data/myntra_products_catalog.csv")
    print(df.head())
