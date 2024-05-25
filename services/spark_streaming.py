from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, BooleanType, LongType, IntegerType
import logging
import os

spark = (
    SparkSession.builder.appName("WikipediaStreamProcessor")
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0")
    .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoint")
    .getOrCreate()
)

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s (%(asctime)s): %(message)s (Line %(lineno)d [%(filename)s])", datefmt="%d/%m/%Y %H:%M:%S"
)


schema = StructType(
    [
        StructField("domain", StringType(), True),
        StructField("uri", StringType(), True),
        StructField("user_is_bot", BooleanType(), True),
        StructField("user_id", LongType(), True),
        StructField("user_name", StringType(), True),
        StructField("title", StringType(), True),
        StructField("page_id", LongType(), True),
        StructField("dt", StringType(), True),
    ]
)

kafka_bootstrap_servers = os.environ["KAFKA_BOOTSTRAP_SERVERS"]
input_topic_name = os.environ["WIKI_EVENTS_TOPIC"]

input_stream = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers)
    .option("subscribe", input_topic_name)
    .option("startingOffsets", "earliest")
    .load()
    .selectExpr("CAST(value AS STRING) as json")
)

logging.info(f"{input_stream.printSchema() = }")

json_df = input_stream.select(from_json(col("json"), schema).alias("data"))
json_df.printSchema()


parsed_stream = json_df.select("data.*")

# Print the stream to the console
query = parsed_stream.writeStream.format("console").outputMode("append").start()

query.awaitTermination()
