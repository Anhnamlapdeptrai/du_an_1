#!/bin/bash

NETWORK_NAME="your-network"  # Thay đổi tên mạng nếu cần

# SỬA Ở ĐÂY: Sử dụng đường dẫn tuyệt đối hoặc biến $HOME
COMPOSE_FILES=(
    "/home/lapnguyen/du_an/airflow/docker-compose.yml"
    "/home/lapnguyen/du_an/Transform/kafka-csv-project/docker-compose.yml"
    "/home/lapnguyen/du_an/Extract/docker-compose.yml"
    "/home/lapnguyen/du_an/Transform/kafka-csv-project/docker-compose.producer.yml"
)

# Kiểm tra xem docker có đang chạy không
echo "🔍 Kiểm tra network '$NETWORK_NAME'..."
if ! docker network ls | grep -q "$NETWORK_NAME"; then
    echo "🚧 Network chưa có. Tạo mới..."
    docker network create "$NETWORK_NAME"
else
    echo "✅ Network đã tồn tại."
fi

echo "🔧 Cập nhật các file docker-compose..."

for FILE in "${COMPOSE_FILES[@]}"; do
    # Trước khi kiểm tra hoặc sửa đổi file, hãy kiểm tra sự tồn tại của nó
    if [ ! -f "$FILE" ]; then
        echo "❌ Lỗi: Không tìm thấy file docker-compose tại '$FILE'. Bỏ qua file này."
        continue # Bỏ qua file hiện tại và chuyển sang file tiếp theo
    fi

    if grep -q "name: $NETWORK_NAME" "$FILE"; then
        echo "✅ $FILE đã dùng network $NETWORK_NAME"
    else
        echo "⚙️  Thêm network config vào $FILE"
        # Đảm bảo bạn có quyền ghi vào file này
        cat <<EOF >> "$FILE"

networks:
  default:
    external: true
    name: $NETWORK_NAME
EOF
    fi
done

echo "🎉 Xong! Tất cả các file đã gắn vào network '$NETWORK_NAME'"