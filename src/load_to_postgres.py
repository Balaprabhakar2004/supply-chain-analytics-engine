import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))


def load_table(conn, csv_path, table_name, columns):
    df = pd.read_csv(csv_path)
    cur = conn.cursor()

    cur.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY")

    cols_str = ', '.join(columns)
    placeholders = ', '.join(['%s'] * len(columns))
    insert_sql = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"

    rows = df[columns].values.tolist()
    cur.executemany(insert_sql, rows)
    conn.commit()
    print(f"Loaded {len(rows)} rows into {table_name}")


if __name__ == '__main__':
    conn = get_connection()

    load_table(conn, 'data/processed/by_region.csv', 'region_stats',
               ['order_region', 'total_orders', 'total_sales', 'avg_order_value'])

    load_table(conn, 'data/processed/late_by_mode.csv', 'shipping_mode_stats',
               ['shipping_mode', 'total_shipments', 'late_risk_pct', 'avg_days_actual', 'avg_days_scheduled'])

    load_table(conn, 'data/processed/by_category.csv', 'category_stats',
               ['category_name', 'total_orders', 'total_sales'])

    load_table(conn, 'data/processed/by_status.csv', 'status_stats',
               ['order_status', 'order_count'])

    conn.close()
    print("All aggregation tables loaded.")