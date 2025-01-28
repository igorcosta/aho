from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from typing import Optional, List, Dict, Any

class GoogleDriveTool:
    def __init__(self, credentials_json: str):
        self.creds = Credentials.from_authorized_user_file(credentials_json, ["https://www.googleapis.com/auth/drive"])
        self.service = build("drive", "v3", credentials=self.creds)

    def list_files(self, query: Optional[str] = None, page_size: int = 10) -> List[Dict[str, Any]]:
        try:
            results = self.service.files().list(q=query, pageSize=page_size, fields="files(id, name)").execute()
            return results.get("files", [])
        except Exception as e:
            raise RuntimeError(f"Google Drive API error: {e}")

    def upload_file(self, file_path: str, mime_type: str, folder_id: Optional[str] = None) -> Dict[str, Any]:
        try:
            file_metadata = {"name": file_path.split("/")[-1]}
            if folder_id:
                file_metadata["parents"] = [folder_id]

            media = MediaFileUpload(file_path, mimetype=mime_type)
            file = self.service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            return file
        except Exception as e:
            raise RuntimeError(f"Error uploading file to Google Drive: {e}")

    def download_file(self, file_id: str, output_path: str):
        try:
            request = self.service.files().get_media(fileId=file_id)
            with open(output_path, "wb") as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
            return output_path
        except Exception as e:
            raise RuntimeError(f"Error downloading file from Google Drive: {e}")