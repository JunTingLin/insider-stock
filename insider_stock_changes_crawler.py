import requests
from bs4 import BeautifulSoup

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

    response = requests.post(url, data=data)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 找到表格
    table = soup.find_all('table', class_='hasBorder')[0]

    # 擷取數據
    extracted_data = []
    for i, row in enumerate(table.find_all('tr')):
        # 檢查索引是否在指定的範圍內
        if any(i in range(start, start + 5) for start in range(2, 93, 6)) or i == 98:
            cols = row.find_all('td')
            selected_cols = [cols[j].text.strip() for j in [0, 1, 2, 4]]

            # 將最後一列的字串處理並加總
            numbers_str = selected_cols[-1]
            numbers = numbers_str.split()
            sum_numbers = sum(int(num.replace(',', '')) for num in numbers)

            # 如果加總不為0，則將該行添加到數據列表
            if sum_numbers != 0:
                selected_cols.append(sum_numbers)
                extracted_data.append(selected_cols)
    
    return extracted_data

# 使用函數示例
data = fetch_insider_stock_changes(112, 12, '2330')
for row in data:
    print(row)
