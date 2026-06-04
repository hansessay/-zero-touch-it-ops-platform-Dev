from app.audit import write_audit
from app.integrations.jumpcloud import get_devices, get_users


def fleet_compliance():
    devices_result = get_devices()
    devices = devices_result["devices"]

    compliant_devices = []
    non_compliant_devices = []

    for device in devices:
        checks = {
            "encryption": device.get("encryption") is True,
            "sentinelone": device.get("sentinelone") is True
        }

        device_report = {
            "hostname": device["hostname"],
            "checks": checks,
            "status": "compliant" if all(checks.values()) else "non_compliant"
        }

        if device_report["status"] == "compliant":
            compliant_devices.append(device_report)
        else:
            non_compliant_devices.append(device_report)

    result = {
        "workflow": "fleet_compliance",
        "total_devices": len(devices),
        "compliant_count": len(compliant_devices),
        "non_compliant_count": len(non_compliant_devices),
        "compliant_devices": compliant_devices,
        "non_compliant_devices": non_compliant_devices,
        "status": "completed"
    }

    write_audit("fleet_compliance", "completed", result)

    return result


def identity_compliance():
    users_result = get_users()
    users = users_result["users"]

    compliant_users = []
    non_compliant_users = []

    for user in users:
        checks = {
            "mfa_enabled": user.get("mfa") is True
        }

        user_report = {
            "email": user["email"],
            "checks": checks,
            "status": "compliant" if all(checks.values()) else "non_compliant"
        }

        if user_report["status"] == "compliant":
            compliant_users.append(user_report)
        else:
            non_compliant_users.append(user_report)

    result = {
        "workflow": "identity_compliance",
        "total_users": len(users),
        "compliant_count": len(compliant_users),
        "non_compliant_count": len(non_compliant_users),
        "compliant_users": compliant_users,
        "non_compliant_users": non_compliant_users,
        "status": "completed"
    }

    write_audit("identity_compliance", "completed", result)

    return result