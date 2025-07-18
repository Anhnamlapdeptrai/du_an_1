FROM python:3.11-slim

# 🛠️ Cài công cụ hệ thống + Java
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 🌍 Thiết lập biến môi trường Java cho PySpark
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# 🗂️ Tạo thư mục làm việc
WORKDIR /app

# 📦 Copy toàn bộ project
COPY . .

# 🐍 Cài thư viện Python
RUN pip install --no-cache-dir pyspark python-dotenv kafka-python

# 🚀 Lệnh mặc định nếu cần
CMD tail -f /dev/null
