import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os

def send_email(subject, body, recipient_emails, sender_email, sender_password):
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


def send_report_email(year, month, file_name, file_url, folder_url, recipient_emails, sender_email, sender_password):
    logging.info("正在發送郵件")
    print("正在發送郵件")

    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template', 'html_body_template.html')

    # 從 HTML 文件讀取模板
    with open(template_path, 'r', encoding='utf-8') as file:
        html_body_template = file.read()

    # 格式化 HTML 內容
    html_body = html_body_template.format(year=year, month=month, folder_url=folder_url, file_url=file_url, file_name=file_name)
    # 發送郵件
    send_email(f"{year}年{month}月份 內部人持股異動報告", html_body, recipient_emails, sender_email, sender_password)

