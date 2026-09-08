import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION'),
    )


def upload_file(s3, local_path, s3_key):
    bucket = os.getenv('S3_BUCKET_NAME')
    file_size_mb = os.path.getsize(local_path) / (1024 * 1024)
    print(f"Uploading {local_path} ({file_size_mb:.2f} MB) → s3://{bucket}/{s3_key}")
    s3.upload_file(local_path, bucket, s3_key)
    print("Done.")


if __name__ == '__main__':
    s3 = get_s3_client()

    # Raw data
    upload_file(s3, 'data/raw/dataco_supply_chain.csv', 'raw/dataco_supply_chain.csv')

    # Processed data
    upload_file(s3, 'data/processed/cleaned_orders.parquet', 'processed/cleaned_orders.parquet')

    # Aggregation results
    for name in ['by_region', 'late_by_mode', 'by_category', 'by_status']:
        upload_file(s3, f'data/processed/{name}.csv', f'processed/aggregations/{name}.csv')

    print("\nAll files uploaded to S3 successfully.")