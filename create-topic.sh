#!/bin/bash

TOPIC_NAME=du_an_dau
PARTITIONS=3
REPLICATION_FACTOR=1
BROKER_PORT=9092

echo "🥹 Đang tạo topic mới trong Kafka..."

docker exec -it kafka-2 bash -c "../../bin/kafka-topics \
  --create \
  --topic ${TOPIC_NAME} \
  --partitions ${PARTITIONS} \
  --replication-factor ${REPLICATION_FACTOR} \
  --bootstrap-server localhost:${BROKER_PORT}"

# Kiểm tra kết quả
if [ $? -eq 0 ]; then
  echo "🤨 Topic '${TOPIC_NAME}' được tạo thành công."
else
  echo "🐷 Lỗi khi tạo topic '${TOPIC_NAME}'. Có thể đã tồn tại?"
fi

echo "📋 Danh sách topic hiện tại:"
docker exec -it kafka-2 bash -c "../../bin/kafka-topics --list --bootstrap-server localhost:${BROKER_PORT}"
