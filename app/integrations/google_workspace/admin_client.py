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
    service_account_file = os.environ["GOOGLE_SERVICE_ACCOUNT_FILE"]
    delegated_admin = os.environ["GOOGLE_WORKSPACE_ADMIN"]

    creds = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=SCOPES,
    )

    delegated_creds = creds.with_subject(delegated_admin)

    return build(
        "admin",
        "directory_v1",
        credentials=delegated_creds,
    )


def list_users(max_results: int = 10):
    service = get_directory_service()

    result = service.users().list(
        customer="my_customer",
        maxResults=max_results,
        orderBy="email",
    ).execute()

    return result.get("users", [])


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

    result = service.users().insert(body=body).execute()

    return {
        "system": "Google Workspace",
        "action": "create_user",
        "email": email,
        "department": department,
        "google_id": result.get("id"),
        "primary_email": result.get("primaryEmail"),
        "status": "success",
    }


def suspend_google_user(email: str):
    service = get_directory_service()

    service.users().update(
        userKey=email,
        body={"suspended": True},
    ).execute()

    return {
        "system": "Google Workspace",
        "action": "suspend_user",
        "email": email,
        "status": "success",
    }


def add_user_to_group(
    user_email: str,
    group_email: str,
):
    service = get_directory_service()

    body = {
        "email": user_email,
        "role": "MEMBER",
    }

    service.members().insert(
        groupKey=group_email,
        body=body,
    ).execute()

    return {
        "system": "Google Workspace",
        "action": "add_user_to_group",
        "user_email": user_email,
        "group_email": group_email,
        "status": "success",
    }

def remove_user_from_all_groups(email: str):
    service = get_directory_service()

    groups_result = service.groups().list(
        userKey=email
    ).execute()

    groups = groups_result.get("groups", [])

    removed_groups = []

    for group in groups:
        group_email = group.get("email")

        try:
            service.members().delete(
                groupKey=group_email,
                memberKey=email,
            ).execute()

            removed_groups.append({
                "group": group_email,
                "status": "removed",
            })

        except Exception as error:
            removed_groups.append({
                "group": group_email,
                "status": "failed",
                "error": str(error),
            })

    result = {
        "system": "Google Workspace",
        "action": "remove_user_from_all_groups",
        "email": email,
        "removed_groups": removed_groups,
        "groups_removed_count": len([
            group for group in removed_groups
            if group.get("status") == "removed"
        ]),
        "status": "success",
    }

    write_audit(
        "google_remove_user_from_all_groups",
        "success",
        result,
    )

    return result