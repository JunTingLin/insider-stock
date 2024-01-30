import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import configparser

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
            print("郵件已成功發送")
    except Exception as e:
        print(f"發送郵件時出現錯誤: {e}")

    

# 使用範例
send_email("Test Subject", "This is a test email", "10355098@st.thsh.tp.edu.tw")
