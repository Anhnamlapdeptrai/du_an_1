import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json,col
import logging
import os
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType
logging.basicConfig(level=logging.INFO, # mức độ ghi log
                    format='%(asctime)s:%(funcName)s:%(levelname)s:%(message)s', # định dạng log thời gian , tên hàm, mức độ log và thông điệp
                    datefmt='%Y-%m-%d %H:%M:%S', # định dạng thời gian
                    filename='streaming.log', # ghi log vào file
                    filemode='a', # chế độ ghi đè vào file
                    encoding='utf-8' # mã hóa utf-8
)
logger = logging.getLogger(__name__) # tạo logger với tên của module hiện tại, logname = stream1.py
from dotenv import load_dotenv
load_dotenv()

def create_spark_session():
    try:
        # 📥 Lấy biến từ .env
        app_name = os.getenv("APP_NAME")
        cassandra_host = os.getenv("CASSANDRA_HOST")
        cassandra_port = os.getenv("CASSANDRA_PORT")
        cassandra_user = os.getenv("CASSANDRA_USER")
        cassandra_password = os.getenv("CASSANDRA_PASSWORD")
        cassandra_version = os.getenv("CASSANDRA_CONNECTOR_VERSION")
        kafka_version = os.getenv("KAFKA_CONNECTOR_VERSION")
        scala_version = os.getenv("SCALA_VERSION")

        # 🧩 Ghép chuỗi jar
        jars = ",".join([
            f"com.datastax.spark:spark-cassandra-connector_{scala_version}:{cassandra_version}",
            f"org.apache.spark:spark-sql-kafka-0-10_{scala_version}:{kafka_version}"
        ])

        # 🚀 Tạo SparkSession
        spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.jars.packages", jars) \
            .config("spark.cassandra.connection.host", cassandra_host) \
            .config("spark.cassandra.connection.port", cassandra_port) \
            .config("spark.cassandra.auth.username", cassandra_user) \
            .config("spark.cassandra.auth.password", cassandra_password) \
            .getOrCreate()

        spark.sparkContext.setLogLevel("ERROR")
        logging.info("✅ Spark session created successfully.")
        return spark

    except Exception as e:
        logging.error(f"❌ Couldn't create Spark session: {e}")
        return None
def create_initial_dataframe(spark_session):
    try:
        # 📥 Lấy biến từ .env
        kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
        kafka_topic = os.getenv("KAFKA_TOPIC")

        # 🧩 Định nghĩa schema
        schema = StructType([
            StructField("Ngay", StringType(), True),
            StructField("GiaDieuChinh", DoubleType(), True),
            StructField("GiaDongCua", DoubleType(), True),
            StructField("ThayDoi", StringType(), True),  # dạng chuỗi vì có dấu %
            StructField("KhoiLuongKhopLenh", LongType(), True),
            StructField("GiaTriKhopLenh", LongType(), True),
            StructField("KLThoaThuan", LongType(), True),
            StructField("GtThoaThuan", LongType(), True),
            StructField("GiaMoCua", DoubleType(), True),
            StructField("GiaCaoNhat", DoubleType(), True),
            StructField("GiaThapNhat", DoubleType(), True),
            StructField("code", StringType(), True)
        ])

        # 🚀 Tạo DataFrame từ Kafka
        df = spark_session.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
            .option("subscribe", kafka_topic) \
            .option("startingOffsets", "earliest") \
            .load()
        
        # 🧩 Chuyển đổi dữ liệu từ Kafka
        df = df.selectExpr("CAST(value AS STRING)") \
            .select(from_json(col("value"), schema).alias("data")) \
            .select("data.*")
        # 📜 Giải thích:
        """
        - `from_json` dùng để phân tích cú pháp chuỗi JSON thành các cột
        vd : {"name": "Trí", "age": 18} ,
        data = StructType([
            StructField("name", StringType()),
            StructField("age", IntegerType()    )
        ])
        - `col("value")` lấy cột `value` từ DataFrame Kafka
        - `alias("data")` đặt tên cho cột mới là `data`
        - `select("data.*")` chọn tất cả các cột từ cột `data`
        - `selectExpr("CAST(value AS STRING)")` chuyển đổi dữ liệu từ Kafka sang chuỗi trong đó CAST là hàm chuyển đổi kiểu dữ liệu
        - code đảm bảo rằng dữ liệu từ Kafka được chuyển đổi thành DataFrame với các cột đã định nghĩa trong schema.
        """
        # # 🧩 Đặt tên cột
        # df = df.toDF("id", "name", "age", "city")
    
        # 🚀 Hiển thị thông tin DataFrame
        df.printSchema()
        logging.info(f"✅ Initial streaming DataFrame schema created successfully.")
        return df

    except Exception as e:
        logging.error(f"❌ Couldn't create initial DataFrame: {e}")
        return None
def start_streaming(df):
    # 🚀 Bắt đầu streaming
    """    - `writeStream` là phương thức để ghi dữ liệu streaming
    - `format("org.apache.spark.sql.cassandra")` chỉ định định dạng ghi là Cassandra
    - `outputMode("append")` chỉ định chế độ ghi là thêm mới
    - `options(table="random_names", keyspace="spark_streaming")` chỉ định bảng và keyspace trong Cassandra
    - `start()` bắt đầu quá trình ghi dữ liệu streaming
    """
    my_query = (df.writeStream
                .format("org.apache.spark.sql.cassandra")
                .outputMode("append")
                .options(table="random_names", keyspace="spark_streaming")\
                .start())

    return my_query.awaitTermination()
def write_streaming_data():
    spark = create_spark_session()
    df = create_initial_dataframe(spark)
    if df is None:
        logging.error("❌ Failed to create initial DataFrame. Exiting.")
        return
    start_streaming(df)


if __name__ == '__main__':
    write_streaming_data()