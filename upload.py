from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import logging

# 設置權限範圍
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def login_google_drive():
    creds = None
    # 使用服務帳戶的 JSON 憑證
    creds = service_account.Credentials.from_service_account_file('service-account-file.json', scopes=SCOPES)

    return build('drive', 'v3', credentials=creds)

def upload_file_to_drive(filename, filepath, mimetype, folder_id):
    service = login_google_drive()
    file_metadata = {
        'name': filename,
        'parents': [folder_id]  # 指定文件夾 ID
    }
    media = MediaFileUpload(filepath, mimetype=mimetype)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get("id")
    print(f'File ID: {file_id} has been uploaded')
    logging.info(f'File ID: {file_id} has been uploaded')
    return file_id

def delete_file_from_drive(file_id):
    service = login_google_drive()
    try:
        service.files().delete(fileId=file_id).execute()
        print(f'File with ID: {file_id} has been deleted.')
    except Exception as e:
        print(f'An error occurred: {e}')

def list_files_in_drive(service):
    # Call the Drive v3 API
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))



# folder_id = '<your_folder_id>'
# upload_file_to_drive('example.xlsx', './example.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', folder_id)
# service = login_google_drive()
# list_files_in_drive(service)
# delete_file_from_drive('<your_file_id>')
