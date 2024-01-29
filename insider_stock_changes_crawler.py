import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from fake_useragent import UserAgent
import logging
from datetime import datetime
import twstock

# 設置日誌配置
logging.basicConfig(filename='log.txt', 
                    filemode='a', # a: append, w: overwrite
                    format='%(asctime)s: %(message)s', 
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO,
                    encoding='utf-8')

def safe_request(url, data):
    # 生成隨機的 User-Agent
    ua = UserAgent()
    headers = {'User-Agent': ua.random}

    try:
        response = requests.post(url, data=data, headers=headers)
        # 檢查是否因為請求過多而被限制
        if "Overrun" in response.text or "Too many query requests" in response.text or "Forbidden - 查詢過於頻繁" in response.text:
            logging.info("請求過多，暫停1分鐘")
            print("請求過多，暫停1分鐘")
            time.sleep(60)  # 暫停1分鐘
            return safe_request(url, data)
        return response
    except Exception as e:
        logging.error(f"請求錯誤: {e}")
        print(f"請求錯誤: {e}")
        time.sleep(60)  # 出錯時暫停1分鐘
        return safe_request(url, data)  # 重試請求


def fetch_insider_stock_changes(year, month, co_id):
    url = 'https://mops.twse.com.tw/mops/web/ajax_query6_1'
    data = {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'off': 1,
        'co_id': co_id,
        'year': year,
        'month': month,
        'KIND': 1 # 例如2880華南金就爬第一個即可
    }

    response = safe_request(url, data)

    # 將表格保存為 HTML 文件
    with open(f"tables/response_{co_id}_{year}_{month}.html", "w", encoding='utf-8') as file:
        file.write(str(response.text))

    soup = BeautifulSoup(response.text, 'html.parser')

    # 找到表格
    table = soup.find_all('table', class_='hasBorder')[0]

    # 擷取數據
    extracted_data = []
    rows = table.find_all('tr')
    for i in range(2, len(rows), 6):
        section = rows[i:i + 5]  # 取出每個區塊的5個欄
        for row in section:
            cols = row.find_all('td')
            if cols:  # 確保該欄有數據
                selected_cols = [cols[j].text.strip() for j in [0, 1, 2, 4] if j < len(cols)]

                # 將最後一欄的字串處理並加總
                numbers_str = selected_cols[-1]
                numbers = numbers_str.split()
                sum_numbers = sum(int(num.replace(',', '')) for num in numbers)

                # 將最後一欄字串改用斜線分隔
                selected_cols[-1] = '/'.join(numbers)

                # 如果加總不為0，則將該列添加到數據列表
                if sum_numbers != 0:
                    selected_cols.append(sum_numbers)
                    extracted_data.append(selected_cols)
    
    return extracted_data

def convert_to_dataframe(data):
    # 將數據轉換為 DataFrame
    df = pd.DataFrame(data, columns=['身份別', '姓名', '持股種類', '自有集中/自有其它/私募股數/信託股數/質權股數', '本月增加股數總合'])
    return df


def fetch_taiwan_stock_codes():
    logging.info("正在獲取所有台股代號")
    print("正在獲取所有台股代號")

    # 更新股票代號資料庫
    twstock.__update_codes()

    # 獲取所有台灣上市櫃公司的股票代號
    stock_codes = twstock.twse

    # 篩選出類型為「股票」或「普通股」的代號
    valid_stock_codes = [code for code, info in stock_codes.items() if info.type in ['股票', '普通股']]

    return valid_stock_codes


def fetch_all_insider_stock_changes(year, month):
    logging.info(f"開始爬取數據: {year}年 {month}月")
    print(f"開始爬取數據: {year}年 {month}月")

    # 獲取所有台股代號
    stock_codes = fetch_taiwan_stock_codes()
    # stock_codes = stock_codes[:3]  # 為了範例只取前3個
    total_stocks = len(stock_codes)

    # 初始化一個空的 DataFrame 來存放所有數據
    all_data = pd.DataFrame()

    # 遍歷每個股票代號
    for index, code in enumerate(stock_codes):
        try:
            # 計算並打印進度
            progress = (index + 1) / total_stocks * 100
            logging.info(f"正在爬取股票 {code} ({progress:.2f}%)")
            print(f"正在爬取股票 {code} ({progress:.2f}%)")

            # 獲取該股票代號的內部人員股票變動數據
            insider_data = fetch_insider_stock_changes(year, month, code)

            # 如果有數據，轉換成 DataFrame 並添加到總表中
            if insider_data:
                df = convert_to_dataframe(insider_data)
                df['股票代號'] = code  # 在 DataFrame 中添加股票代號列
                all_data = pd.concat([all_data, df], ignore_index=True)

            # 每次請求後暫停一段時間
            time.sleep(1.67)  # 每 5 秒最多 3 個請求，因此每次請求間隔約 1.67 秒
        
        except Exception as e:
            logging.error(f"處理代碼 {code} 時出錯: {e}")
            print(f"處理代碼 {code} 時出錯: {e}")
            # 出錯時保存當前進度
            all_data.to_excel("combined_data_partial.xlsx", index=False, encoding='utf_8_sig')


    # 調整列的順序，將股票代號列移至最前面
    cols = ['股票代號'] + [col for col in all_data.columns if col != '股票代號']
    all_data = all_data[cols]

    logging.info("數據爬取完成")
    print("數據爬取完成")

    return all_data


# 使用函數示例
year = 112
month = 12
combined_data = fetch_all_insider_stock_changes(year, month)
combined_data.to_excel("combined_data.xlsx", index=False)
logging.info("已將數據保存到 combined_data.xlsx")
print("已將數據保存到 combined_data.xlsx")
