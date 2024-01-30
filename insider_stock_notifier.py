import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import configparser
import logging

def send_email(subject, body, recipient_emails):
    config = configparser.ConfigParser()
    config.read('config.ini')

    sender_email = config['EMAIL']['User']
    sender_password = config['EMAIL']['Pass']

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipient_emails)  # 將收件人列表轉換為以逗號分隔的字串
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))  # 設置 MIME 為 text/html

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.ehlo()
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            logging.info("郵件已成功發送")
            print("郵件已成功發送")
    except Exception as e:
        logging.error(f"發送郵件時出現錯誤: {e}")
        print(f"發送郵件時出現錯誤: {e}")


# 確保已經有適當的日誌配置設定
logging.basicConfig(filename='log.txt', 
                    filemode='a',  # a: append, w: overwrite
                    format='%(asctime)s: %(message)s', 
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO,
                    encoding='utf-8')
