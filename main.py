import logger_config
from data_fetch import fetch_all_insider_stock_changes
from data_process import save_dataframe_to_excel_with_timestamp
from email_notify import send_report_email
from date_utils import get_previous_month_year


# 設置日誌
logger_config.setup_logging()

# 獲取上個月的年份和月份
year, month = get_previous_month_year()
# year, month = '113', '12'

combined_data = fetch_all_insider_stock_changes(year, month)
file_name = save_dataframe_to_excel_with_timestamp(combined_data, year, month)
if file_name:
    send_report_email(year, month, file_name)
