import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

from app.audit import write_audit


SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.user",
    "https://www.googleapis.com/auth/admin.directory.group",
    "https://www.googleapis.com/auth/admin.directory.group.member",
]


def get_directory_service():
    service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    delegated_admin = os.getenv("GOOGLE_WORKSPACE_ADMIN")

    if not service_account_file:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_FILE is not set")

    if not delegated_admin:
        raise RuntimeError("GOOGLE_WORKSPACE_ADMIN is not set")

    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=SCOPES,
    )

    delegated_credentials = credentials.with_subject(delegated_admin)

    return build("admin", "directory_v1", credentials=delegated_credentials)


def create_google_user(
    first_name: str,
    last_name: str,
    email: str,
    department: str,
):
    service = get_directory_service()

    body = {
        "primaryEmail": email,
        "name": {
            "givenName": first_name,
            "familyName": last_name,
        },
        "password": "ChangeMe123!",
        "changePasswordAtNextLogin": True,
        "orgUnitPath": "/",
        "organizations": [
            {
                "department": department,
                "primary": True,
            }
        ],
    }

    created_user = service.users().insert(body=body).execute()

    result = {
        "system": "Google Workspace",
        "action": "create_user",
        "email": email,
        "department": department,
        "google_id": created_user.get("id"),
        "status": "success",
    }

    write_audit("google_create_user", "success", result)
    return result


def suspend_google_user(email: str):
    service = get_directory_service()

    updated_user = service.users().update(
        userKey=email,
        body={"suspended": True},
    ).execute()

    result = {
        "system": "Google Workspace",
        "action": "suspend_user",
        "email": email,
        "suspended": updated_user.get("suspended"),
        "status": "success",
    }

    write_audit("google_suspend_user", "success", result)
    return result


def add_user_to_group(user_email: str, group_email: str):
    service = get_directory_service()

    member = {
        "email": user_email,
        "role": "MEMBER",
    }

    created_member = service.members().insert(
        groupKey=group_email,
        body=member,
    ).execute()

    result = {
        "system": "Google Workspace",
        "action": "add_user_to_group",
        "user_email": user_email,
        "group_email": group_email,
        "member_id": created_member.get("id"),
        "status": "success",
    }

    write_audit("google_add_user_to_group", "success", result)
    return result