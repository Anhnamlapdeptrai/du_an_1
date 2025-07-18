import requests
from bs4 import BeautifulSoup
import pandas as pd
import os


def get_data(code="FPT", page=1):
    print(f"Đang lấy dữ liệu: {code}, trang {page}")

    URL = f"https://s.cafef.vn/Lich-su-giao-dich-{code}-1.chn"
    headers = {
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "X-MicrosoftAjax": "Delta=true",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept": "*/*",
    "Origin": "https://s.cafef.vn",
    "Referer": "https://cafef.vn/du-lieu/lich-su-giao-dich-fpt-1.chn",
    "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
    }
    cookies = {
        "__uidac": "01674af08bfaa8138021712fa20f9210",
        "__adm_upl": "eyJ0aW1lIjoxNzMyOTY0NDk3LCJfdXBsIjpudWxsfQ==",
        "dtdz": "_PID.1.8946673e9d8a50b6",
        "_dtdcTime": "1732964492",
        "__R": "3",
        "favorite_stocks_state": "1",
        "__tb": "0",
        "__RC": "5",
        "_uidcms": "1924426392885330312",
        "__admUTMtime": "1748917635",
        "favorite_stocks": "FBA",
        "__utmz": "56744888.1749116286.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)",
        "_gid": "GA1.2.2097032804.1751022059",
        "__IP": "3075501833",
        "__utma": "56744888.793374598.1732964492.1751023257.1751027872.3",
        "ChannelVN.Logger": "1751027872286",
        "ChannelVN.Logger.p": "0_1751027872286",
        "ChannelVN.Logger.c": "1117_1751027872287",
        "ASP.NET_SessionId": "42qtnzytvfqdclnuzyiygabu",
        "_admcfr": "624784_4%2C625801_3%2C625309_1",
        "_ga": "GA1.1.793374598.1732964492",
        "__uif": "__uid%3A1924426392885330312%7C__ui%3A1%252C5%7C__create%3A1732442639",
        "_ga_XLBBV02H03": "GS2.1.s1751098443$o12$g1$t1751099468$j49$l0$h0",
        "_ga_860L8F5EZP": "GS2.1.s1751098339$o13$g1$t1751099468$j49$l0$h0",
        "_ga_D40MBMET7Z": "GS2.1.s1751098443$o12$g1$t1751099468$j49$l0$h0"
    }
    body = {
            "ctl00$ContentPlaceHolder1$scriptmanager": "ctl00$ContentPlaceHolder1$ctl03$panelAjax|ctl00$ContentPlaceHolder1$ctl03$pager2",
            "ctl00$ContentPlaceHolder1$ctl03$txtKeyword": code,
            "ctl00$ContentPlaceHolder1$ctl03$dpkTradeDate1$txtDatePicker": "",
            "ctl00$ContentPlaceHolder1$ctl03$dpkTradeDate2$txtDatePicker": "",
            "__EVENTTARGET": "ctl00$ContentPlaceHolder1$ctl03$pager2",
            "__EVENTARGUMENT": str(page),
            "__VIEWSTATE": "viewstate",
            "__VIEWSTATEGENERATOR": "viewstategen",
            "__ASYNCPOST": "true",
        }
    try:
        res = requests.post(URL, headers=headers, cookies=cookies, data=body, timeout=10)
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu {code} trang {page}: {e}")
        return pd.DataFrame()

    soup = BeautifulSoup(res.content, 'html.parser')
    table_tag = soup.find('table', id='GirdTable2')
    if not table_tag:
        print(f"Không tìm thấy bảng cho {code}, trang {page}")
        return pd.DataFrame()

    rows = []
    for row in table_tag.find_all('tr')[2:]:
        cols = row.find_all('td')
        if len(cols) < 12:
            continue

        def _str_to_float(s):
            return float(s.encode('utf-8').decode('utf-8').replace('\xa0', '').replace(',', '').replace('(', '').replace(' %)', '').strip())

        change_price_value, _, change_price_percent = cols[3].get_text().partition(" ")

        rows.append({
            "code": code,
            "date": cols[0].get_text().strip(),
            "modificable_price": _str_to_float(cols[1].get_text()),
            "close_price": _str_to_float(cols[2].get_text()),
            "change_price_value": _str_to_float(change_price_value),
            "change_price_percent": _str_to_float(change_price_percent),
            "KL_GD_khoplenh": _str_to_float(cols[5].get_text()),
            "GT_GD_khoplenh": _str_to_float(cols[6].get_text()),
            "KL_GD_thoathuan": _str_to_float(cols[7].get_text()),
            "GT_GD_thoathuan": _str_to_float(cols[8].get_text()),
            "open_price": _str_to_float(cols[9].get_text()),
            "highest_price": _str_to_float(cols[10].get_text()),
            "lowest_price": _str_to_float(cols[11].get_text()),
        })

    return pd.DataFrame(rows)


def get_all_data(code="FPT"):
    os.makedirs("data-all", exist_ok=True)
    save_path = f"data-all/{code}.csv"

    try:
        df = pd.read_csv(save_path)
    except:
        df = pd.DataFrame()

    all_data = []
    for page in range(1, 300):
        df_page = get_data(code, page)
        if df_page.empty:
            break
        all_data.append(df_page)

    if all_data:
        new_data = pd.concat(all_data, ignore_index=True)
        if not df.empty:
            new_data = pd.concat([df, new_data], ignore_index=True)
        new_data = new_data.drop_duplicates(subset=["date"]).reset_index(drop=True)
        new_data.to_csv(save_path, index=False)
        print(f"Đã lưu {save_path}")
    else:
        print(f"Không có dữ liệu mới cho {code}")
if __name__ == "__main__":
    codes = ["FPT", "VHM", "HPG"]  # Thay bằng danh sách mã bạn muốn cào

    for code in codes:
        get_all_data(code)
        print(f"Đã hoàn thành cào dữ liệu cho {code}")
    print("Hoàn thành cào dữ liệu cho tất cả các mã.")