FROM openjdk:17-slim

# Cài Python + tool cần thiết
RUN apt-get update && apt-get install -y \
    python3 python3-pip netcat-openbsd \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set Python mặc định (symlink nếu chưa có)
RUN [ ! -e /usr/bin/python ] && ln -s /usr/bin/python3 /usr/bin/python || true

# JAVA_HOME cho PySpark
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH
ENV PYSPARK_SUBMIT_ARGS="--driver-java-home=/usr/lib/jvm/java-17-openjdk-amd64 pyspark-shell"

# Cài thư viện Python
RUN pip install --no-cache-dir \
    pyspark==3.5.1 \
    kafka-python \
    python-dotenv

# Copy source
WORKDIR /app
COPY . .

# Container chạy giữ cho sống
CMD ["tail", "-f", "/dev/null"]
