from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# 設置權限範圍
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def login_google_drive():
    creds = None
    # 使用服務帳戶的 JSON 憑證
    creds = service_account.Credentials.from_service_account_file('service-account-file.json', scopes=SCOPES)

    return build('drive', 'v3', credentials=creds)

def upload_file_to_drive(filename, filepath, mimetype):
    service = login_google_drive()
    file_metadata = {'name': filename}
    media = MediaFileUpload(filepath, mimetype=mimetype)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f'File ID: {file.get("id")}')

def delete_file_from_drive(file_id):
    service = login_google_drive()
    try:
        service.files().delete(fileId=file_id).execute()
        print(f'File with ID: {file_id} has been deleted.')
    except Exception as e:
        print(f'An error occurred: {e}')

# 上傳檔案示例
upload_file_to_drive('example.xlsx', './example.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
