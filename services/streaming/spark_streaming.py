from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, count, date_format, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, BooleanType, LongType
import logging
import os
from functools import partial


logging.basicConfig(
    level=logging.INFO, format="%(levelname)s (%(asctime)s): %(message)s (Line %(lineno)d [%(filename)s])", datefmt="%d/%m/%Y %H:%M:%S"
)

spark = (
    SparkSession.builder.appName("WikipediaStreamProcessor")
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.5.0",
    )
    .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoint")
    .config("spark.cassandra.connection.host", os.environ["CASSANDRA_HOST"])
    .config("spark.cassandra.connection.port", os.environ["CASSANDRA_PORT"])
    .getOrCreate()
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
json_df_with_date = json_df.withColumn("date", date_format(to_timestamp(col("data.dt"), "yyyy-MM-dd'T'HH:mm:ss'Z'"), "yyyy-MM-dd"))

json_df.printSchema()


def write_to_cassandra(batch_df, _, keyspace, table):
    batch_df.write.format("org.apache.spark.sql.cassandra").options(table=table, keyspace=keyspace).mode("append").save()


write_to_wiki_cassandra = partial(write_to_cassandra, keyspace="wikipedia")

write_user_pages = partial(write_to_wiki_cassandra, table="user_pages")
write_unique_domains = partial(write_to_wiki_cassandra, table="unique_domains")
write_page_information = partial(write_to_wiki_cassandra, table="page_information")
write_domain_pages = partial(write_to_wiki_cassandra, table="domain_pages")
write_active_users_by_date = partial(write_to_wiki_cassandra, table="active_users_by_date")

query_console = json_df.select("data.*").writeStream.format("console").outputMode("append").start()
query_unique_domains = json_df.select("data.domain").writeStream.outputMode("update").foreachBatch(write_unique_domains).start()
query_user_pages = json_df.select("data.user_id", "data.page_id").writeStream.outputMode("append").foreachBatch(write_user_pages).start()
query_page_information = (
    json_df.select("data.page_id", "data.uri", "data.title").writeStream.outputMode("append").foreachBatch(write_page_information).start()
)
query_domain_pages = (
    json_df.groupBy("data.domain")
    .agg(count("data.page_id").alias("num_pages"))
    .writeStream.outputMode("update")
    .foreachBatch(write_domain_pages)
    .start()
)
query_active_users_by_date = (
    json_df_with_date.groupBy("date", "data.user_id", "data.user_name")
    .agg(count("data.page_id").alias("num_created_pages"))
    .writeStream.outputMode("update")
    .foreachBatch(write_active_users_by_date)
    .start()
)


query_console.awaitTermination()
query_unique_domains.awaitTermination()
query_user_pages.awaitTermination()
query_page_information.awaitTermination()
query_domain_pages.awaitTermination()
query_active_users_by_date.awaitTermination()
