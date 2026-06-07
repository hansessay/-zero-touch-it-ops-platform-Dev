import os
import requests

from app.audit import write_audit

JUMPCLOUD_API_V1 = "https://console.eu.jumpcloud.com/api"
JUMPCLOUD_API_V2 = "https://console.eu.jumpcloud.com/api/v2"


def _headers():
    api_key = os.getenv("JUMPCLOUD_API_KEY")

    if not api_key:
        raise RuntimeError("Missing JUMPCLOUD_API_KEY environment variable")

    return {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _parse_response(response):
    try:
        return response.json()
    except Exception:
        return response.text


def create_jumpcloud_user(
    first_name: str,
    last_name: str,
    email: str,
    department: str,
):
    payload = {
        "firstname": first_name,
        "lastname": last_name,
        "email": email,
        "username": email.split("@")[0],
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
        "response": _parse_response(response),
    }

    write_audit("jumpcloud_get_users", "completed", result)
    return result


def get_devices():
    response = requests.get(
        f"{JUMPCLOUD_API_V1}/systems",
        headers=_headers(),
        timeout=30,
    )

    result = {
        "system": "JumpCloud",
        "action": "get_devices",
        "status_code": response.status_code,
        "response": _parse_response(response),
    }

    write_audit("jumpcloud_get_devices", "completed", result)
    return result


def suspend_user(email: str):
    result = {
        "system": "JumpCloud",
        "action": "suspend_user",
        "email": email,
        "status": "not_implemented_yet",
    }

    write_audit("jumpcloud_suspend_user", "completed", result)
    return result


def run_command(
    command_name: str,
    target_group: str,
    script_type: str,
):
    result = {
        "system": "JumpCloud",
        "action": "run_command",
        "command_name": command_name,
        "target_group": target_group,
        "script_type": script_type,
        "status": "api_ready_placeholder",
    }

    write_audit("jumpcloud_run_command", "completed", result)
    return result


def apply_policy(
    policy_name: str,
    target_group: str,
    policy_type: str,
):
    result = {
        "system": "JumpCloud",
        "action": "apply_policy",
        "policy_name": policy_name,
        "target_group": target_group,
        "policy_type": policy_type,
        "status": "api_ready_placeholder",
    }

    write_audit("jumpcloud_apply_policy", "completed", result)
    return result