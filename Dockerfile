FROM python:3.10-slim

# Java is required for PySpark
RUN apt-get update && \
    apt-get install -y openjdk-21-jre-headless && \
    apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/raw/ ./data/raw/

RUN mkdir -p data/processed

# Runs the full pipeline in sequence: clean → aggregate → upload to S3 → load to Postgres
CMD ["sh", "-c", "python src/clean.py && python src/aggregate.py && python src/upload_to_s3.py && python src/load_to_postgres.py"]