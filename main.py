import logger_config
from data_fetch import fetch_all_insider_stock_changes
from data_process import save_dataframe_to_excel_with_timestamp
from email_notify import send_report_email
from date_utils import get_previous_month_year
from upload import upload_file_to_drive
import configparser
import os


config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config_env.ini')
config.read(config_path)
recipient_emails = config['RECIPIENTS']['Emails'].split(', ')
sender_email = config['EMAIL']['User']
sender_password = config['EMAIL']['Pass']
folder_id = config['DATA']['FolderID']
folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 設置日誌
logger_config.setup_logging()

# 獲取上個月的年份和月份
year, month = get_previous_month_year()
# year, month = '113', '12'

combined_data = fetch_all_insider_stock_changes(year, month, output_dir)
file_name = save_dataframe_to_excel_with_timestamp(combined_data, year, month, output_dir)

if file_name:
    file_path = os.path.join(output_dir, file_name)
    # 上傳檔案到 Google Drive，並獲取上傳後的檔案ID
    file_id = upload_file_to_drive(file_name, file_path, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', folder_id)
    file_url = f"https://drive.google.com/file/d/{file_id}/view"
    send_report_email(year, month, file_name, file_url, folder_url, recipient_emails, sender_email, sender_password)
