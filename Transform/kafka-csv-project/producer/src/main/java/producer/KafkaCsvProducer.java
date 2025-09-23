package producer;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerRecord;
import java.util.Properties;
import org.apache.commons.csv.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Map;
import java.util.HashMap;
import java.io.*;

public class KafkaCsvProducer {

    public static void main(String[] args) {
        Properties props = new Properties();
        props.put("bootstrap.servers", "kafka:9092");
        props.put("linger.ms", 1);
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("acks", "all");
        props.put("retries", 3);
        props.put("batch.size", 32_768);
        props.put("max.block.ms", 1000);
        props.put("compression.type", "gzip");
        props.put("enable.idempotence", "true");
        props.put("max.in.flight.requests.per.connection", 5);

        Producer<String, String> producer = new KafkaProducer<>(props); // tạo producer vs data là string 
        ObjectMapper objectMapper = new ObjectMapper();

        try (
            Reader reader = new FileReader("/app/data/FPT.csv"); 
            CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT.withFirstRecordAsHeader());// định dạng theo pandas của python
        ) {
            int count = 0;
            for (CSVRecord record : csvParser) {
                String Ngay = record.get("Ngay"); // dùng ngày làm key
                // chuyển qua làm json 
                Map<String, String> rowMap = new HashMap<>();
                for (String header : csvParser.getHeaderNames()) {
                    rowMap.put(header, record.get(header));
                }

                String jsonValue = objectMapper.writeValueAsString(rowMap);
                String topic = "du_an_dau";

                System.out.println(" 😏 Đang gửi record số " + (++count));
                System.out.println(" 😱  Key: " + Ngay);
                System.out.println(" 👻  Value: " + jsonValue);

                ProducerRecord<String, String> producerRecord = new ProducerRecord<>(topic, Ngay, jsonValue);
                producer.send(producerRecord, (metadata, exception) -> {
                    if (exception != null) {
                        System.out.println(" Gửi lỗi: " + exception.getMessage());
                    } else {
                        System.out.println(" 🌚 Gửi thành công! Topic: " + metadata.topic() +
                                           ", Partition: " + metadata.partition() +
                                           ", Offset: " + metadata.offset());
                    }
                });

                Thread.sleep(100); // chậm lại để dễ nhìn log
            }
        } catch (IOException e) {
            System.err.println("🤡 File IO lỗi: " + e.getMessage());
            e.printStackTrace();
        } catch (InterruptedException e) {
            System.err.println("😴 Lỗi sleep: " + e.getMessage());
        }

        producer.flush();
        producer.close();
        System.out.println("🌚 Đã gửi xong toàn bộ dữ liệu từ CSV.");
    }
}
