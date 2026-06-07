import os
import base64
import requests
from app.audit import write_audit

JUMPCLOUD_API_V1 = "https://console.jumpcloud.com/api"
JUMPCLOUD_API_V2 = "https://console.jumpcloud.com/api/v2"
JUMPCLOUD_TOKEN_URL = "https://admin-oauth.id.jumpcloud.com/oauth2/token"


def _get_access_token():
    client_id = os.getenv("JUMPCLOUD_CLIENT_ID")
    client_secret = os.getenv("JUMPCLOUD_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise RuntimeError("Missing JUMPCLOUD_CLIENT_ID or JUMPCLOUD_CLIENT_SECRET")

    raw = f"{client_id}:{client_secret}"
    encoded = base64.b64encode(raw.encode()).decode()

    response = requests.post(
        JUMPCLOUD_TOKEN_URL,
        headers={
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "scope": "api",
            "grant_type": "client_credentials",
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(f"JumpCloud token failed: {response.status_code} {response.text}")

    return response.json()["access_token"]


def _headers():
    token = _get_access_token()
    org_id = os.getenv("JUMPCLOUD_ORG_ID")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    if org_id:
        headers["x-org-id"] = org_id

    return headers


def _parse_response(response):
    try:
        return response.json()
    except Exception:
        return response.text


def get_users():
    response = requests.get(
        f"{JUMPCLOUD_API_V1}/systemusers",
        headers=_headers(),
        timeout=30,
    )

    result = {
        "system": "JumpCloud",
        "action": "get_users",
        "status_code": response.status_code,
        "users": _parse_response(response),
    }

    write_audit("jumpcloud_get_users", "completed", result)
    return result


def get_devices():
    response = requests.get(
        f"{JUMPCLOUD_API_V2}/systems",
        headers=_headers(),
        timeout=30,
    )

    result = {
        "system": "JumpCloud",
        "action": "get_devices",
        "status_code": response.status_code,
        "devices": _parse_response(response),
    }

    write_audit("jumpcloud_get_devices", "completed", result)
    return result


def create_jumpcloud_user(first_name: str, last_name: str, email: str, department: str):
    payload = {
        "firstname": first_name,
        "lastname": last_name,
        "email": email,
        "username": email,
        "department": department,
        "activated": True,
    }

    response = requests.post(
        f"{JUMPCLOUD_API_V1}/systemusers",
        headers=_headers(),
        json=payload,
        timeout=30,
    )

    result = {
        "system": "JumpCloud",
        "action": "create_user",
        "email": email,
        "status_code": response.status_code,
        "response": _parse_response(response),
    }

    write_audit("jumpcloud_create_user", "completed", result)
    return result