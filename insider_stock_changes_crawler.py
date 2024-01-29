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

def fetch_first_day_close_price(year, month, stock_code):
    logging.info(f"正在獲取 {stock_code} 的當月收盤價")
    print(f"正在獲取 {stock_code} 的當月收盤價")
    # 創建一個 Stock 物件
    stock = twstock.Stock(stock_code)

    # 將民國年轉換為西元年
    year += 1911

    # 獲取指定年月的股票交易資料
    stock_data = stock.fetch_from(year, month)

    if stock_data:
        first_day_data = stock_data[0]
        first_day_close_price = first_day_data.close
        return first_day_close_price
    else:
        logging.warning(f"無法獲取 {stock_code} 的當月收盤價")
        print(f"無法獲取 {stock_code} 的當月收盤價")
        return None


def fetch_all_insider_stock_changes(year, month):
    logging.info(f"開始爬取數據: {year}年 {month}月")
    print(f"開始爬取數據: {year}年 {month}月")

    # 獲取所有台股代號
    stock_codes = fetch_taiwan_stock_codes()
    # stock_codes = stock_codes[:20]  # 為了範例只取前20個
    total_stocks = len(stock_codes)

    # 初始化一個空的 DataFrame 來存放所有數據
    all_data = pd.DataFrame()
    last_code = None  # 用於儲存上一個股票的代號
    last_closing_price = None  # 用於儲存上一個股票的收盤價

    save_interval = 100  # 每處理100個股票代號後保存一次

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

                # 檢查是否為新的股票代號
                if code != last_code:
                    last_closing_price = fetch_first_day_close_price(year, month, code)
                    last_code = code

                df['當月收盤價'] = last_closing_price
                if df['當月收盤價'] is not None:
                    df['本月增加股數總合'] = df['本月增加股數總合'].replace({',': ''}, regex=True).astype(float)
                    df['持股增加金額'] = df['本月增加股數總合'] * df['當月收盤價']
                else:
                    df['持股增加金額'] = None

                all_data = pd.concat([all_data, df], ignore_index=True)

                # 每處理指定數量的股票代號後保存一次
                if (index + 1) % save_interval == 0:
                    all_data.to_excel(f"{year}_{month}_temp.xlsx", index=False, encoding='utf_8_sig')
                    logging.info(f"已將中途數據保存")
                    print(f"已將中途數據保存")

            else:
                logging.warning(f"股票 {code} 本月增加股數總合為 0")
                print(f"股票 {code} 本月增加股數總合為 0")
                

            # 每次請求後暫停一段時間
            time.sleep(1.67)  # 每 5 秒最多 3 個請求，因此每次請求間隔約 1.67 秒

        except KeyboardInterrupt:
        # 當使用者中斷程式時，執行以下代碼
            logging.warning("用戶中斷了程式，保存當前數據")
            print("用戶中斷了程式，保存當前數據")
            all_data.to_excel("{year}_{month}_temp.xlsx", index=False, encoding='utf_8_sig')
            raise  # 可以選擇再次引發異常，或者直接結束程式
        
        except Exception as e:
            logging.error(f"處理代碼 {code} 時出錯: {e}")
            print(f"處理代碼 {code} 時出錯: {e}")
            # 出錯時保存當前進度
            all_data.to_excel("{year}_{month}_temp.xlsx", index=False, encoding='utf_8_sig')


    adjusted_data = process_and_sort_dataframe(all_data, '股票代號')

    logging.info("數據爬取完成")
    print("數據爬取完成")

    return adjusted_data

def process_and_sort_dataframe(df, primary_col):
    # 調整行的順序，將指定行移至最前面
    cols = [primary_col] + [col for col in df.columns if col != primary_col]
    df = df[cols]

    # 移除所有欄位完全相同的重複記錄
    df = df.drop_duplicates()

    # 按照「持股增加金額」降序排序
    df = df.sort_values(by='持股增加金額', ascending=False)

    return df


def save_dataframe_to_excel_with_timestamp(df, year, month):
    # 生成包含時間戳記的檔案名稱
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{year}_{month}_insider_stock_changes_{timestamp}.xlsx"
    
    try:
        df.to_excel(file_name, index=False)
        print(f"數據已成功保存到 {file_name}")
        logging.info(f"數據已成功保存到 {file_name}")
    except Exception as e:
        print(f"保存數據時出錯: {e}")
        logging.error(f"保存數據時出錯: {e}")

# 使用函數示例
year = 112
month = 12
combined_data = fetch_all_insider_stock_changes(year, month)
save_dataframe_to_excel_with_timestamp(combined_data, year, month)
