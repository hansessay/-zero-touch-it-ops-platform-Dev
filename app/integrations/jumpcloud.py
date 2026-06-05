import os
import requests
from app.audit import write_audit


JUMPCLOUD_API_KEY = os.getenv("JUMPCLOUD_API_KEY")
JUMPCLOUD_BASE_URL = "https://console.jumpcloud.com/api/v2"


def _headers():
    print("JumpCloud API key loaded:", bool(JUMPCLOUD_API_KEY))

    return {
        "x-api-key": JUMPCLOUD_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


def create_jumpcloud_user(first_name: str, last_name: str, email: str, department: str):
    payload = {
        "firstname": first_name,
        "lastname": last_name,
        "email": email,
        "department": department,
        "activated": True
    }

    response = requests.post(
        "https://console.jumpcloud.com/api/systemusers",
        headers=_headers(),
        json=payload,
        timeout=30
    )

    try:
        response_body = response.json()
    except Exception:
        response_body = response.text

    result = {
        "system": "JumpCloud",
        "action": "create_user",
        "email": email,
        "status_code": response.status_code,
        "response": response_body
    }

    write_audit("jumpcloud_create_user", "completed", result)
    return result


def suspend_user(email: str):
    result = {
        "system": "JumpCloud",
        "action": "suspend_user",
        "email": email,
        "status": "api_ready_placeholder"
    }

    write_audit("jumpcloud_suspend_user", "completed", result)
    return result


def get_devices():
    response = requests.get(
        f"{JUMPCLOUD_BASE_URL}/systems",
        headers=_headers(),
        timeout=30
    )

    result = {
        "system": "JumpCloud",
        "action": "get_devices",
        "status_code": response.status_code,
        "devices": response.json() if response.text else []
    }

    write_audit("jumpcloud_get_devices", "completed", result)
    return result


def get_users():
    response = requests.get(
        "https://console.jumpcloud.com/api/systemusers",
        headers=_headers(),
        timeout=30
    )

    try:
        response_body = response.json()
    except Exception:
        response_body = response.text

    result = {
        "system": "JumpCloud",
        "action": "get_users",
        "status_code": response.status_code,
        "users": response_body
    }

    write_audit("jumpcloud_get_users", "completed", result)
    return result


def run_command(command_name: str, target_group: str, script_type: str):
    result = {
        "system": "JumpCloud",
        "action": "run_command",
        "command_name": command_name,
        "target_group": target_group,
        "script_type": script_type,
        "status": "api_ready_placeholder"
    }

    write_audit("jumpcloud_run_command", "completed", result)
    return result


def apply_policy(policy_name: str, target_group: str, policy_type: str):
    result = {
        "system": "JumpCloud",
        "action": "apply_policy",
        "policy_name": policy_name,
        "target_group": target_group,
        "policy_type": policy_type,
        "status": "api_ready_placeholder"
    }

    write_audit("jumpcloud_apply_policy", "completed", result)
    return result