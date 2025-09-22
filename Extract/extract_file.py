import requests
import pandas as pd
import os
import time
def get_data_json(symbol="FPT", page=1, retries=5, delay=1):
    print(f"💪 Đang lấy {symbol}, trang {page}")
    url = ".https://cafef.vn/du-lieu/Ajax/PageNew/DataHistory/PriceHistory.ashx"
    params = {
        "Symbol": symbol,
        "PageIndex": page,
        "PageSize": 20
    }

    for attempt in range(retries):
        try:
            res = requests.get(url, params=params, timeout=20) # timeout là thời gian chờ tối đa
            res.raise_for_status()  # Gây lỗi nếu mã status != 200

            data = res.json()
            if not data.get("Success", False): # nếu ko có key thì mặc định là False
                print(f" 👏 Dữ liệu không thành công với {symbol}, trang {page}")
                return pd.DataFrame()

            rows = data.get("Data", {}).get("Data", [])
            if not rows:
                print(f"Không có dữ liệu tại {symbol}, trang {page}")
                return pd.DataFrame()

            df = pd.DataFrame(rows)
            df["code"] = symbol
            time.sleep(delay)  # 💤 Nghỉ sau mỗi lần thành công
            return df

        except Exception as e:
            print(f" 🙏 Lỗi '{e}' – thử lại lần {attempt + 1}/{retries}")
            time.sleep(delay + 1)  # nghỉ lâu hơn một chút khi có lỗi

    print(f" Thất bại sau {retries} lần thử với {symbol}, trang {page}")
    return pd.DataFrame()


def get_all_data(symbol="FPT", page=60):
    os.makedirs("/opt/airflow/Transform/kafka-csv-project/data", exist_ok=True)
    save_path = f"/opt/airflow/Transform/kafka-csv-project/data/{symbol}.csv"

    try:
        old_df = pd.read_csv(save_path)
    except:
        old_df = pd.DataFrame()

    all_pages = []
    for page in range(1, page+1):
        df_page = get_data_json(symbol, page)
        if df_page.empty:
            break
        all_pages.append(df_page)

    if all_pages:
        new_df = pd.concat(all_pages, ignore_index=True) 
        full_df = pd.concat([old_df, new_df], ignore_index=True)
        full_df = full_df.drop_duplicates(subset=["Ngay"]).reset_index(drop=True)# drop_duplicates giữ lại bản ghi đầu tiên, sau đó reset index,nếu không có dữ liệu mới thì sẽ không ghi đè lên file cũ,subset=["Ngay"] là cột ngày, nếu có dữ liệu mới thì sẽ ghi đè lên file cũ
        full_df.to_csv(save_path, index=False) 
        print(f" 👽 Đã lưu dữ liệu {symbol} vào {save_path}")
    else:
        print(f"Không có dữ liệu mới cho {symbol}")


if __name__ == "__main__":
    get_all_data("FPT")
    print("😵‍💫 Hoàn tất!")
