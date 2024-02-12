import logging
from datetime import datetime
import os

def setup_logging():
    # 創建 logs 目錄如果它不存在
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # 使用 strftime 方法格式化當前時間，創建合法的文件名
    now = datetime.now().strftime("%Y%m%d_%H%M%S")    
    log_filename = f"{now}.log"

    # 完整的日誌文件路徑
    log_filepath = os.path.join(logs_dir, log_filename)

    # 設置日誌配置
    logging.basicConfig(filename=log_filepath,
                        filemode='w',  # a: append, w: overwrite
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO,
                        encoding='utf-8')
    
    