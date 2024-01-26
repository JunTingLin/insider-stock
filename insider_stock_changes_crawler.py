import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from fake_useragent import UserAgent

def fetch_insider_stock_changes(year, month, co_id):
    url = 'https://mops.twse.com.tw/mops/web/ajax_query6_1'
    data = {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'off': 1,
        'co_id': co_id,
        'year': year,
        'month': month
    }

    # 生成隨機的 User-Agent
    ua = UserAgent()
    headers = {'User-Agent': ua.random}

    response = requests.post(url, data=data,  headers=headers)
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
                if sum_numbers == 0:
                    selected_cols.append(sum_numbers)
                    extracted_data.append(selected_cols)
    
    return extracted_data

def convert_to_dataframe(data):
    # 將數據轉換為 DataFrame
    df = pd.DataFrame(data, columns=['身份別', '姓名', '持股種類', '自有集中/自有其它/私募股數/信託股數/質權股數', '本月增加總合'])
    return df


def fetch_taiwan_stock_codes():
    # 從網站獲取數據
    res = requests.get("http://isin.twse.com.tw/isin/C_public.jsp?strMode=2")
    df = pd.read_html(res.text)[0]

    # 設定column名稱並清理數據
    df.columns = df.iloc[0]  # 將第一行設為列名
    df = df.iloc[2:]  # 移除前兩行
    df = df.reset_index(drop=True)  # 重設索引

    # 分割「有價證券代號及名稱」列為兩個獨立列
    df[['有價證券代號', '名稱']] = df['有價證券代號及名稱'].str.split('\u3000', expand=True)
    df.drop('有價證券代號及名稱', axis=1, inplace=True)  # 移除原始列

    # 調整列的順序
    cols = ['有價證券代號', '名稱'] + [col for col in df.columns if col not in ['有價證券代號', '名稱']]
    df = df[cols]

    # 篩選出所有四位數字的股票代號
    valid_stock_codes = df['有價證券代號'][df['有價證券代號'].str.match(r'^\d{4}$')].tolist()

    return valid_stock_codes

def fetch_all_insider_stock_changes(year, month):
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
            print(f"\r正在爬取股票 {code} ({progress:.2f}%)", end='')

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
            print(f"處理代碼 {code} 時出錯: {e}")
            # 出錯時保存當前進度
            all_data.to_excel("combined_data_partial.xlsx", index=False, encoding='utf_8_sig')


    # 調整列的順序，將股票代號列移至最前面
    cols = ['股票代號'] + [col for col in all_data.columns if col != '股票代號']
    all_data = all_data[cols]

    return all_data


# 使用函數示例
year = 112
month = 12
combined_data = fetch_all_insider_stock_changes(year, month)
combined_data.to_excel("combined_data.xlsx", index=False)
print("數據爬取完成！並已將數據保存到 combined_data.xlsx")
