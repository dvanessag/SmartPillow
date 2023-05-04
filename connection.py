from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Set the path to your service account key file
KEY_FILE_LOCATION = 'path/to/key.json'

# Set the API scope and the name of the file you want to upload
SCOPES = ['https://www.googleapis.com/auth/drive']
FILE_NAME = 'example.txt'




# Authenticate with Google using your service account key file
creds = service_account.Credentials.from_service_account_file(
    KEY_FILE_LOCATION, scopes=SCOPES)

# Create a Drive API client
drive_service = build('drive', 'v3', credentials=creds)

# Upload the file to Google Drive
file_metadata = {'name': FILE_NAME}
media = MediaFileUpload(FILE_NAME, resumable=True)
file = drive_service.files().create(body=file_metadata, media_body=media,
                                     fields='id').execute()
print(f'File ID: {file.get("id")}')
