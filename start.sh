#!/bin/bash

COMPOSE_FILES=(
    "/home/lapnguyen/du_an/airflow-2/docker-compose.yml"
    "/home/lapnguyen/du_an/Transform/kafka-csv-project/docker-compose.yml"
    "/home/lapnguyen/du_an/Extract/docker-compose.yml"
)

echo "🔄 Đang khởi động các dịch vụ Docker..."

for file in "${COMPOSE_FILES[@]}"; do
  echo "🚀 Đang khởi động: $file"
  docker-compose -f "$file" up -d

  if [ $? -ne 0 ]; then
    echo "❌ Lỗi khi khởi động $file. Dừng script."
    exit 1
  fi
done

echo "✅ Tất cả dịch vụ đã được khởi động thành công."
