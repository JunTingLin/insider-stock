from datetime import datetime, timedelta

def get_previous_month_year():
    today = datetime.today()
    first_day_of_current_month = datetime(today.year, today.month, 1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    # 使用 strftime 格式化月份，確保月份為兩位數
    year_str = str(last_day_of_previous_month.year - 1911)
    month_str = last_day_of_previous_month.strftime("%m")  # "%m" 會自動補零
    return year_str, month_str
