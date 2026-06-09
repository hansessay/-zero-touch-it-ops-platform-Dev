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


def _result(action, status_code, response, extra=None):
    data = {
        "system": "JumpCloud",
        "action": action,
        "status": "success" if status_code in [200, 201, 204] else "failed",
        "status_code": status_code,
        "response": response,
    }

    if extra:
        data.update(extra)

    audit_status = "completed" if status_code in [200, 201, 204] else "failed"
    write_audit(f"jumpcloud_{action}", audit_status, data)

    return data


def get_users():
    response = requests.get(
        f"{JUMPCLOUD_API_V1}/systemusers",
        headers=_headers(),
        timeout=30,
    )

    return _result("get_users", response.status_code, _parse_response(response))


def get_devices():
    response = requests.get(
        f"{JUMPCLOUD_API_V1}/systems",
        headers=_headers(),
        timeout=30,
    )

    return _result("get_devices", response.status_code, _parse_response(response))


def create_jumpcloud_user(first_name, last_name, email, department):
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

    return _result(
        "create_user",
        response.status_code,
        _parse_response(response),
        {"email": email},
    )


def find_user_by_email(email):
    users = get_users()
    results = users.get("response", {}).get("results", [])

    for user in results:
        if user.get("email", "").lower() == email.lower():
            return user

    return None


def suspend_user(email):
    user = find_user_by_email(email)

    if not user:
        return {
            "system": "JumpCloud",
            "action": "suspend_user",
            "email": email,
            "status": "user_not_found",
        }

    user_id = user.get("_id") or user.get("id")

    payload = {
        "suspended": True,
    }

    response = requests.put(
        f"{JUMPCLOUD_API_V1}/systemusers/{user_id}",
        headers=_headers(),
        json=payload,
        timeout=30,
    )

    return _result(
        "suspend_user",
        response.status_code,
        _parse_response(response),
        {"email": email, "user_id": user_id},
    )


def get_device_by_id(device_id):
    response = requests.get(
        f"{JUMPCLOUD_API_V1}/systems/{device_id}",
        headers=_headers(),
        timeout=30,
    )

    return _result(
        "get_device_by_id",
        response.status_code,
        _parse_response(response),
        {"device_id": device_id},
    )


def find_device_by_hostname(hostname):
    devices = get_devices()
    results = devices.get("response", {}).get("results", [])

    for device in results:
        display_name = device.get("displayName", "")
        system_hostname = device.get("hostname", "")

        if hostname.lower() in [display_name.lower(), system_hostname.lower()]:
            return device

    return None


def get_user_groups():
    response = requests.get(
        f"{JUMPCLOUD_API_V2}/usergroups",
        headers=_headers(),
        timeout=30,
    )

    return _result("get_user_groups", response.status_code, _parse_response(response))


def get_device_groups():
    response = requests.get(
        f"{JUMPCLOUD_API_V2}/systemgroups",
        headers=_headers(),
        timeout=30,
    )

    return _result("get_device_groups", response.status_code, _parse_response(response))


def get_policies():
    response = requests.get(
        f"{JUMPCLOUD_API_V2}/policies",
        headers=_headers(),
        timeout=30,
    )

    return _result("get_policies", response.status_code, _parse_response(response))


def get_commands():
    response = requests.get(
        f"{JUMPCLOUD_API_V1}/commands",
        headers=_headers(),
        timeout=30,
    )

    return _result("get_commands", response.status_code, _parse_response(response))


def run_command(command_name, target_group, script_type):
    result = {
        "system": "JumpCloud",
        "action": "run_command",
        "command_name": command_name,
        "target_group": target_group,
        "script_type": script_type,
        "status": "api_ready_requires_command_id",
    }

    write_audit("jumpcloud_run_command", "completed", result)
    return result


def apply_policy(policy_name, target_group, policy_type):
    result = {
        "system": "JumpCloud",
        "action": "apply_policy",
        "policy_name": policy_name,
        "target_group": target_group,
        "policy_type": policy_type,
        "status": "api_ready_requires_policy_id",
    }

    write_audit("jumpcloud_apply_policy", "completed", result)
    return result