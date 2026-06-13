from dotenv import load_dotenv
load_dotenv()

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


def _get_items(response_data):
    if isinstance(response_data, list):
        return response_data

    if isinstance(response_data, dict):
        return response_data.get("results", [])

    return []


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

    response = requests.put(
        f"{JUMPCLOUD_API_V1}/systemusers/{user_id}",
        headers=_headers(),
        json={"suspended": True},
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


def find_policy_by_name(policy_name):
    policies = get_policies()
    items = _get_items(policies.get("response"))

    for policy in items:
        name = policy.get("name") or policy.get("displayName")

        if name and name.lower() == policy_name.lower():
            return policy

    return None


def find_device_group_by_name(group_name):
    groups = get_device_groups()
    items = _get_items(groups.get("response"))

    for group in items:
        name = group.get("name") or group.get("displayName")

        if name and name.lower() == group_name.lower():
            return group

    return None


def add_user_to_group_by_id(user_id, user_group_id):
    payload = {
        "op": "add",
        "type": "user",
        "id": user_id,
    }

    response = requests.post(
        f"{JUMPCLOUD_API_V2}/usergroups/{user_group_id}/members",
        headers=_headers(),
        json=payload,
        timeout=30,
    )

    return _result(
        "add_user_to_group_by_id",
        response.status_code,
        _parse_response(response),
        {"user_id": user_id, "user_group_id": user_group_id},
    )


def add_device_to_group_by_id(device_id, device_group_id):
    payload = {
        "op": "add",
        "type": "system",
        "id": device_id,
    }

    response = requests.post(
        f"{JUMPCLOUD_API_V2}/systemgroups/{device_group_id}/members",
        headers=_headers(),
        json=payload,
        timeout=30,
    )

    return _result(
        "add_device_to_group_by_id",
        response.status_code,
        _parse_response(response),
        {"device_id": device_id, "device_group_id": device_group_id},
    )


def apply_policy_real(policy_name, target_group, policy_type):
    policy = find_policy_by_name(policy_name)
    group = find_device_group_by_name(target_group)

    if not policy:
        return {
            "system": "JumpCloud",
            "action": "apply_policy_real",
            "status": "failed",
            "reason": "policy_not_found",
            "policy_name": policy_name,
        }

    if not group:
        return {
            "system": "JumpCloud",
            "action": "apply_policy_real",
            "status": "failed",
            "reason": "device_group_not_found",
            "target_group": target_group,
        }

    policy_id = policy.get("id") or policy.get("_id")
    group_id = group.get("id") or group.get("_id")

    payload = {
        "op": "add",
        "type": "system_group",
        "id": group_id,
    }

    response = requests.post(
        f"{JUMPCLOUD_API_V2}/policies/{policy_id}/associations",
        headers=_headers(),
        json=payload,
        timeout=30,
    )

    parsed_response = _parse_response(response)

    if response.status_code == 409:
        if isinstance(parsed_response, dict):
            if parsed_response.get("message") == "Already Exists":
                return _result(
                    "apply_policy_real",
                    200,
                    parsed_response,
                    {
                        "policy_name": policy_name,
                        "policy_id": policy_id,
                        "target_group": target_group,
                        "target_group_id": group_id,
                        "policy_type": policy_type,
                        "idempotent": True,
                    },
                )

    return _result(
        "apply_policy_real",
        response.status_code,
        parsed_response,
        {
            "policy_name": policy_name,
            "policy_id": policy_id,
            "target_group": target_group,
            "target_group_id": group_id,
            "policy_type": policy_type,
        },
    )




def apply_policy(policy_name, target_group, policy_type):
    return apply_policy_real(policy_name, target_group, policy_type)


def find_command_by_name(command_name):
    commands = get_commands()
    items = _get_items(commands.get("response"))

    for command in items:
        name = command.get("name") or command.get("displayName")

        if name and name.lower() == command_name.lower():
            return command

    return None


def run_command(command_name, target_group, script_type):
    command = find_command_by_name(command_name)
    group = find_device_group_by_name(target_group)

    if not command:
        return {
            "system": "JumpCloud",
            "action": "run_command",
            "status": "failed",
            "reason": "command_not_found",
            "command_name": command_name,
        }

    if not group:
        return {
            "system": "JumpCloud",
            "action": "run_command",
            "status": "failed",
            "reason": "device_group_not_found",
            "target_group": target_group,
        }

    command_id = command.get("id") or command.get("_id")
    group_id = group.get("id") or group.get("_id")

    payload = {
        "op": "add",
        "type": "system_group",
        "id": group_id,
    }

    response = requests.post(
        f"{JUMPCLOUD_API_V2}/commands/{command_id}/associations",
        headers=_headers(),
        json=payload,
        timeout=30,
    )

    return _result(
        "run_command",
        response.status_code,
        _parse_response(response),
        {
            "command_name": command_name,
            "command_id": command_id,
            "target_group": target_group,
            "target_group_id": group_id,
            "script_type": script_type,
        },
    )