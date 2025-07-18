package consumer;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;

import java.time.Duration;
import java.util.Collections;
import java.util.Properties;

public class Consumer {
    public static void main(String[] args) {
        // Cấu hình Kafka Consumer
        Properties props = new Properties();
        props.put("bootstrap.servers", "kafka:9092"); // Địa chỉ broker
        props.put("group.id", "test-group");              // Nhóm consumer
        props.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        props.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        props.put("auto.offset.reset", "earliest");       // Bắt đầu từ đầu nếu chưa có offset

        // Tạo KafkaConsumer
        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
        consumer.subscribe(Collections.singletonList("du_an_dau")); // Đăng ký topic

        System.out.println("Listening to topic...");

        // Vòng lặp lắng nghe message
        while (true) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(1000)); // Đợi 1s
            for (ConsumerRecord<String, String> record : records) {
                System.out.printf("Nhận được message: key = %s, value = %s, partition = %d, offset = %d%n",
                        record.key(), record.value(), record.partition(), record.offset());
            }
        }
    }
}
