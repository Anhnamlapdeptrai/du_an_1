FROM python:3.11-slim

#  Cài Java Runtime (JRE) thay vì JDK cho nhẹ và không lỗi
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    netcat-openbsd \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


# Thiết lập JAVA_HOME để PySpark nhận Java
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH
ENV PYSPARK_SUBMIT_ARGS="--driver-java-home=/usr/lib/jvm/java-17-openjdk-amd64 pyspark-shell"


# Cài thư viện Python
RUN pip install --no-cache-dir \
    pyspark==3.5.1 \
    kafka-python \
    python-dotenv

#  Copy mã nguồn vào container
WORKDIR /app
COPY . .

# Mặc định chạy chương trình
CMD ["tail -f /dev/null"]
