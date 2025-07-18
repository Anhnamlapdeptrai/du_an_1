FROM maven:3.9.6-eclipse-temurin-17

WORKDIR /app

# Copy project
COPY .. .

# Build code luôn khi tạo image
RUN mvn clean package -DskipTests

# Mặc định bash để dễ chạy thủ công
CMD ["sh", "-c", "java -jar app.jar && tail -f /dev/null"]

