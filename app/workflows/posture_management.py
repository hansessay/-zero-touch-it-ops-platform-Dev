from app.audit import write_audit
from app.integrations.jumpcloud import (
    find_device_by_hostname,
    apply_policy_real,
)


BASELINES = {
    "Engineering": {
        "required_os": "Windows",
        "disk_encryption_required": True,
        "policy_name": "JC Standard Security - Allow The Use of Biometrics",
        "target_group": "Engineering",
        "policy_type": "windows",
    }
}


def check_device_posture(hostname: str, department: str = "Engineering"):
    device = find_device_by_hostname(hostname)
    baseline = BASELINES.get(department)

    if not device:
        return {
            "workflow": "posture_management",
            "hostname": hostname,
            "status": "device_not_found",
        }

    findings = []

    os_name = device.get("os")
    encryption_enabled = device.get("fde", {}).get("active") is True
    policy_bound = device.get("isPolicyBound") is True

    if baseline["required_os"] not in os_name:
        findings.append("Operating system does not match baseline")

    if baseline["disk_encryption_required"] and not encryption_enabled:
        findings.append("Disk encryption is not enabled")

    if not policy_bound:
        findings.append("Device is not policy bound")

    status = "compliant" if not findings else "drift_detected"

    result = {
        "workflow": "posture_management",
        "hostname": hostname,
        "department": department,
        "status": status,
        "findings": findings,
        "actual_state": {
            "os": os_name,
            "disk_encryption_enabled": encryption_enabled,
            "policy_bound": policy_bound,
        },
        "desired_state": baseline,
    }

    write_audit("posture_check", status, result)
    return result


def remediate_device_posture(hostname: str, department: str = "Engineering"):
    posture = check_device_posture(hostname, department)
    baseline = BASELINES.get(department)

    remediation_actions = []

    if posture.get("status") == "device_not_found":
        return posture

    if posture.get("status") == "drift_detected":
        remediation = apply_policy_real(
            policy_name=baseline["policy_name"],
            target_group=baseline["target_group"],
            policy_type=baseline["policy_type"],
        )
        remediation_actions.append(remediation)

    result = {
        "workflow": "posture_remediation",
        "hostname": hostname,
        "department": department,
        "posture_status": posture.get("status"),
        "findings": posture.get("findings", []),
        "remediation_actions": remediation_actions,
        "status": "completed",
    }

    write_audit("posture_remediation", "completed", result)
    return result