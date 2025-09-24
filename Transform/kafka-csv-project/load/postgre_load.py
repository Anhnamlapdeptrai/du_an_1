from kafka import KafkaConsumer
import psycopg2
import json
from datetime import datetime
import re

# --- KAFKA CONSUMER ---
consumer = KafkaConsumer(
    "du_an_dau",
    bootstrap_servers=["kafka:9092"],
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    group_id=None,
    value_deserializer=lambda x: x.decode("utf-8")
)
print("🐘 Consumer đã kết nối. Đang chờ Postgres...")

conn = psycopg2.connect(
    host="postgres",        # trong docker-compose
    database="postgres",
    user="airflow",
    password="airflow",
    port=5432               # port container
)   
cursor = conn.cursor()
print("🙉 Kết nối Postgres thành công.")


insert_query = """
    INSERT INTO stock_prices (
        ngay, code, gia_dieu_chinh, gia_dong_cua, thay_doi_gia, 
        khoi_luong_khop_lenh, gia_tri_khop_lenh, kl_thoa_thuan, gt_thoa_thuan,
        gia_mo_cua, gia_cao_nhat, gia_thap_nhat, thay_doi_phan_tram
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
print("😗 Câu lệnh INSERT đã sẵn sàng.")

for message in consumer:
    print(f"😏 Nhận CSV: {message.value}")
    data = json.loads(message.value)

    ngay = datetime.strptime(data["Ngay"], "%d/%m/%Y").date()

    raw = data["ThayDoi"]  # ví dụ: "-0.1(-0.09 %)"
    match = re.match(r"([-\d\.]+)\(([-\d\.]+)\s*%", raw)
    if match:
        thay_doi_gia = float(match.group(1))           # -0.1
        thay_doi_phan_tram = float(match.group(2))     # -0.09
    else:
        thay_doi_gia = None
        thay_doi_phan_tram = None

    values = (
        ngay,
        data["code"],
        float(data["GiaDieuChinh"]),
        float(data["GiaDongCua"]),
        thay_doi_gia,
        float(data["KhoiLuongKhopLenh"]),
        float(data["GiaTriKhopLenh"]),
        float(data["KLThoaThuan"]),
        float(data["GtThoaThuan"]),
        float(data["GiaMoCua"]),
        float(data["GiaCaoNhat"]),
        float(data["GiaThapNhat"]),
        thay_doi_phan_tram
    )

    cursor.execute(insert_query, values)
    conn.commit()
    print(f"✅ Đã insert")

# Đóng kết nối
cursor.close()
conn.close()
print("🥴 Kết nối Postgres đã đóng.")


