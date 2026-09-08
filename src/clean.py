import pandas as pd

def load_and_clean(input_path):
    df = pd.read_csv(input_path, encoding='latin-1')
    print(f"Raw shape: {df.shape}")

    # Drop PII / irrelevant columns — not needed for analytics, and good
    # practice even on synthetic data
    drop_cols = [
        'Customer Email', 'Customer Password', 'Customer Fname', 'Customer Lname',
        'Customer Street', 'Product Description', 'Product Image', 'Product Status',
        'Customer Zipcode', 'Order Zipcode', 'Latitude', 'Longitude'
    ]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    # Standardize column names to snake_case
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(r'[^\w\s]', '', regex=True)   # remove parentheses etc.
        .str.replace(r'\s+', '_', regex=True)
        .str.lower()
    )

    # Parse date columns (they currently look like "1/1/2018 0:00")
    date_cols = [c for c in df.columns if 'date' in c]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    # Drop rows missing critical fields — can't analyze an order with no date or amount
    before = len(df)
    df = df.dropna(subset=['order_id', 'sales', 'order_date_dateorders'])
    print(f"Dropped {before - len(df)} rows missing critical fields")

    # Fix obviously invalid data: negative sales/quantity shouldn't exist
    df = df[df['sales'] >= 0]
    df = df[df['order_item_quantity'] >= 0]

    print(f"Cleaned shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    return df


if __name__ == '__main__':
    df = load_and_clean('data/raw/dataco_supply_chain.csv')
    df.to_parquet(
    'data/processed/cleaned_orders.parquet',
    index=False,
    coerce_timestamps='us',        # force microsecond precision, Spark-compatible
    allow_truncated_timestamps=True)
    print("Saved cleaned data to data/processed/cleaned_orders.parquet")