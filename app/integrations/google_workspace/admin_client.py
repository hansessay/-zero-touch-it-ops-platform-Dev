import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.user.readonly"
]

def get_directory_service():
    creds = service_account.Credentials.from_service_account_file(
        os.environ["GOOGLE_SERVICE_ACCOUNT_FILE"],
        scopes=SCOPES,
        subject=os.environ["GOOGLE_WORKSPACE_ADMIN"]
    )

    return build("admin", "directory_v1", credentials=creds)


def list_users(max_results=10):
    service = get_directory_service()

    result = service.users().list(
        customer="my_customer",
        maxResults=max_results
    ).execute()

    return result.get("users", [])