import sys
from pyspark.sql.functions import regexp_extract
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json,col
import logging
import os
from pyspark.sql.functions import to_date
from pyspark.sql.functions import split
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType
from pyspark.sql.types import (
    StructType, StructField,
    StringType, DoubleType, LongType,
    TimestampType, DateType   
)
logging.basicConfig(level=logging.INFO, # mức độ ghi log
                    format='%(asctime)s:%(funcName)s:%(levelname)s:%(message)s', # định dạng log thời gian , tên hàm, mức độ log và thông điệp
                    datefmt='%Y-%m-%d %H:%M:%S', # định dạng thời gian
                    filename='oke.log', # ghi log vào file
                    filemode='a', # chế độ ghi đè vào file
                    encoding='utf-8' # mã hóa utf-8
)
logger = logging.getLogger() # tạo logger với tên của module hiện tại, logname = stream1.py
from dotenv import load_dotenv
load_dotenv()

def create_spark_session():
    try:
        # Lấy biến từ .env
        app_name = os.getenv("APP_NAME")
        cassandra_host = os.getenv("CASSANDRA_HOST")
        cassandra_port = os.getenv("CASSANDRA_PORT")
        cassandra_user = os.getenv("CASSANDRA_USER")
        cassandra_password = os.getenv("CASSANDRA_PASSWORD")
        cassandra_version = os.getenv("CASSANDRA_CONNECTOR_VERSION")
        kafka_version = os.getenv("KAFKA_CONNECTOR_VERSION")
        scala_version = os.getenv("SCALA_VERSION")

        #  Ghép chuỗi jar
        jars = ",".join([
            f"com.datastax.spark:spark-cassandra-connector_{scala_version}:{cassandra_version}",
            f"org.apache.spark:spark-sql-kafka-0-10_{scala_version}:{kafka_version}"
        ])


        #  Tạo SparkSession
        spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.jars.packages", jars) \
            .config("spark.cassandra.connection.host", cassandra_host) \
            .config("spark.cassandra.connection.port", cassandra_port) \
            .config("spark.cassandra.auth.username", cassandra_user) \
            .config("spark.cassandra.auth.password", cassandra_password) \
            .getOrCreate()

        spark.sparkContext.setLogLevel("INFO") # nếu ko chạy thì in 
        logging.info("Spark session created successfully.")
        return spark

    except Exception as e:
        logging.error(f" Couldn't create Spark session: {e}")
        return None
def create_initial_dataframe(spark_session):
    try:
        kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
        kafka_topic = os.getenv("KAFKA_TOPIC")

        #  Định nghĩa schema cho JSON
        schema = StructType([
            StructField("Ngay", StringType(), True),          # ban đầu đọc dạng string
            StructField("GiaDieuChinh", StringType(), True),
            StructField("GiaDongCua", StringType(), True),
            StructField("ThayDoi", StringType(), True),       # "0.2(0.40 %)" cần xử lý thêm
            StructField("KhoiLuongKhopLenh", StringType(), True),
            StructField("GiaTriKhopLenh", StringType(), True),
            StructField("KLThoaThuan", StringType(), True),
            StructField("GtThoaThuan", StringType(), True),
            StructField("GiaMoCua", StringType(), True),
            StructField("GiaCaoNhat", StringType(), True),
            StructField("GiaThapNhat", StringType(), True),
            StructField("code", StringType(), True)
        ])

        #  Đọc Kafka
        df = (spark_session.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", kafka_bootstrap_servers)
            .option("subscribe", kafka_topic)
            .option("startingOffsets", "earliest")
            .load())

        #  Parse JSON
        df = df.selectExpr("CAST(value AS STRING) as raw") \
               .withColumn("jsonData", from_json(col("raw"), schema)) \
               .select("jsonData.*")

        #  Chuyển đổi kiểu dữ liệu
        df = df.withColumn("ngay", to_date(col("Ngay"), "dd/MM/yyyy")) \
               .withColumn("giadieuchinh", col("GiaDieuChinh").cast("double")) \
               .withColumn("giadongcua", col("GiaDongCua").cast("double")) \
               .withColumn("khoiluongkhoplenh", col("KhoiLuongKhopLenh").cast("long")) \
               .withColumn("giatrikhoplenh", col("GiaTriKhopLenh").cast("double")) \
               .withColumn("klthoathuan", col("KLThoaThuan").cast("long")) \
               .withColumn("gtthoathuan", col("GtThoaThuan").cast("double")) \
               .withColumn("giamocua", col("GiaMoCua").cast("double")) \
               .withColumn("giacaonhat", col("GiaCaoNhat").cast("double")) \
               .withColumn("giathapnhat", col("GiaThapNhat").cast("double")) \
               .withColumn("thaydoi", regexp_extract(col("ThayDoi"), r"([0-9.]+)", 1).cast("double")) \
               .withColumn("code", col("code"))

        # Lọc key
        df = df.filter(col("code").isNotNull() & col("ngay").isNotNull())
        df = df.dropDuplicates(["code", "ngay"])

        df.printSchema()
        logging.info(" Initial streaming DataFrame schema created successfully (JSON).")
        return df

    except Exception as e:
        logging.error(f" Couldn't create initial DataFrame: {e}")
        return None

def start_streaming(df):
    try:
        query = (df.writeStream
            .format("org.apache.spark.sql.cassandra")
            .outputMode("append")
            .option("checkpointLocation", "/tmp/spark_checkpoints/csdl_anhlap")
            .option("keyspace", "spark_streaming")
            .option("table", "csdl_anhlap")
            .start())
        logging.info(" Streaming query started and writing to Cassandra.")
        query.awaitTermination()
    except Exception as e:
        logging.error(f" Streaming failed: {e}")
    return query.awaitTermination()


def write_streaming_data():
    spark = create_spark_session()
    df = create_initial_dataframe(spark)
    if df is None:
        logging.error(" Failed to create initial DataFrame. Exiting.")
        return
    start_streaming(df)


if __name__ == '__main__':
    write_streaming_data()