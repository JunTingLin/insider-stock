import pandas as pd
from datetime import datetime
import logging


def convert_to_dataframe(data):
    # 將數據轉換為 DataFrame
    df = pd.DataFrame(data, columns=['身份別', '姓名', '持股種類', '本月增加股數(集中市場)'])
    return df

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
        file_name = None  # 如果出現錯誤，返回 None

    return file_name