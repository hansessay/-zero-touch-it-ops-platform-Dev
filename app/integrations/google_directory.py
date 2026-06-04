import os
from app.audit import write_audit

from google.oauth2 import service_account
from googleapiclient.discovery import build


GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
GOOGLE_WORKSPACE_ADMIN = os.getenv("GOOGLE_WORKSPACE_ADMIN")

SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.user",
    "https://www.googleapis.com/auth/admin.directory.group",
    "https://www.googleapis.com/auth/admin.directory.group.member"
]


def _directory_service():
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )

    delegated_credentials = credentials.with_subject(
        GOOGLE_WORKSPACE_ADMIN
    )

    return build(
        "admin",
        "directory_v1",
        credentials=delegated_credentials
    )


def create_google_user(first_name: str, last_name: str, email: str, department: str):
    service = _directory_service()

    payload = {
        "primaryEmail": email,
        "name": {
            "givenName": first_name,
            "familyName": last_name
        },
        "password": "ChangeMe123!",
        "changePasswordAtNextLogin": True,
        "orgUnitPath": "/"
    }

    response = service.users().insert(body=payload).execute()

    result = {
        "system": "Google Workspace",
        "action": "create_user",
        "email": email,
        "department": department,
        "response": response,
        "status": "completed"
    }

    write_audit("google_create_user", "completed", result)
    return result


def suspend_google_user(email: str):
    service = _directory_service()

    response = service.users().update(
        userKey=email,
        body={"suspended": True}
    ).execute()

    result = {
        "system": "Google Workspace",
        "action": "suspend_user",
        "email": email,
        "response": response,
        "status": "completed"
    }

    write_audit("google_suspend_user", "completed", result)
    return result


def add_user_to_group(user_email: str, group_email: str):
    service = _directory_service()

    payload = {
        "email": user_email,
        "role": "MEMBER"
    }

    response = service.members().insert(
        groupKey=group_email,
        body=payload
    ).execute()

    result = {
        "system": "Google Workspace",
        "action": "add_user_to_group",
        "user_email": user_email,
        "group_email": group_email,
        "response": response,
        "status": "completed"
    }

    write_audit("google_add_user_to_group", "completed", result)
    return result


def transfer_drive_ownership(old_owner: str, new_owner: str):
    result = {
        "system": "Google Workspace",
        "action": "transfer_drive_ownership",
        "old_owner": old_owner,
        "new_owner": new_owner,
        "status": "api_ready_placeholder",
        "note": "Drive ownership transfer requires Drive API implementation."
    }

    write_audit("google_transfer_drive_ownership", "completed", result)
    return result