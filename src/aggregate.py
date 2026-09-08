from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum as spark_sum, avg, round as spark_round, when

def create_spark_session():
    return SparkSession.builder \
        .appName("SupplyChainAggregation") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()


def run_aggregations(spark, parquet_path):
    df = spark.read.parquet(parquet_path)
    print(f"Loaded {df.count()} rows into Spark")

    # 1. Sales & order volume by region — a core "where is our business" metric
    by_region = (
        df.groupBy("order_region")
        .agg(
            count("order_id").alias("total_orders"),
            spark_round(spark_sum("sales"), 2).alias("total_sales"),
            spark_round(avg("sales"), 2).alias("avg_order_value"),
        )
        .orderBy(col("total_sales").desc())
    )

    # 2. Late delivery risk by shipping mode — operational efficiency metric,
    # directly relevant to a logistics company
    late_by_mode = (
        df.groupBy("shipping_mode")
        .agg(
            count("order_id").alias("total_shipments"),
            spark_round(avg("late_delivery_risk") * 100, 2).alias("late_risk_pct"),
            spark_round(avg("days_for_shipping_real"), 2).alias("avg_days_actual"),
            spark_round(avg("days_for_shipment_scheduled"), 2).alias("avg_days_scheduled"),
        )
        .orderBy(col("late_risk_pct").desc())
    )

    # 3. Top product categories by sales volume
    by_category = (
        df.groupBy("category_name")
        .agg(
            count("order_id").alias("total_orders"),
            spark_round(spark_sum("sales"), 2).alias("total_sales"),
        )
        .orderBy(col("total_sales").desc())
        .limit(15)
    )

    # 4. Order status breakdown — operational health snapshot
    by_status = (
        df.groupBy("order_status")
        .agg(count("order_id").alias("order_count"))
        .orderBy(col("order_count").desc())
    )

    return {
        "by_region": by_region,
        "late_by_mode": late_by_mode,
        "by_category": by_category,
        "by_status": by_status,
    }


if __name__ == '__main__':
    spark = create_spark_session()
    results = run_aggregations(spark, 'data/processed/cleaned_orders.parquet')

    for name, result_df in results.items():
        print(f"\n=== {name} ===")
        result_df.show(10, truncate=False)
        result_df.toPandas().to_csv(f'data/processed/{name}.csv', index=False)
        print(f"Saved to data/processed/{name}.csv")

    spark.stop()