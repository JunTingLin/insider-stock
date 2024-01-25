import requests
from bs4 import BeautifulSoup

url = 'https://mops.twse.com.tw/mops/web/ajax_query6_1'
data = {
    'encodeURIComponent': 1,
    'step': 1,
    'firstin': 1,
    'off': 1,
    'co_id': '2330',
    'year': 112,
    'month': 12
    
}

response = requests.post(url, data=data)
# print(response.text)
# 假設 html_content 是從網站獲取的 HTML 內容
html_content = response.text  # 或者您從網站獲取的 HTML 內容
soup = BeautifulSoup(html_content, 'html.parser')

# 找到表格
table = soup.find_all('table', class_='hasBorder')[0]

# 擷取數據
data = []
for i, row in enumerate(table.find_all('tr')):
    # 檢查索引是否在指定的範圍內(index2~6、index8~12、...、index92~96、index98)
    if any(i in range(start, start + 5) for start in range(2, 93, 6)) or i == 98 :
        cols = row.find_all('td')
        selected_cols = [cols[j].text.strip() for j in [0, 1, 2, 4]]  # 選擇指定的列
        data.append(selected_cols)

# data 現在包含您所需要的數據
for row in data:
    print(row)
