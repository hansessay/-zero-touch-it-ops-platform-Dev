from app.audit import write_audit
from app.integrations.jumpcloud import (
    find_device_by_hostname,
    apply_policy_real,
    run_command,
)


BASELINES = {
    "Engineering": {
        "required_os": "Windows",
        "disk_encryption_required": True,
        "policy_required": True,
        "security_policy_name": "JC Standard Security - Allow The Use of Biometrics",
        "disk_encryption_policy_name": "JC Standard Security - BitLocker Full Disk Encryption",
        "target_group": "Engineering",
        "policy_type": "windows",
        "remediation_commands": {
            "firewall": "Re-enable Windows Firewall",
            "patching": "Check Windows Update Status",
            "sentinelone": "Check SentinelOne Agent Status",
        },
    }
}


def _safe_get_os(device: dict):
    return (
        device.get("os")
        or device.get("osName")
        or device.get("systemOS")
        or ""
    )


def check_device_posture(hostname: str, department: str = "Engineering"):
    device = find_device_by_hostname(hostname)
    baseline = BASELINES.get(department)

    if not baseline:
        return {
            "workflow": "posture_management",
            "hostname": hostname,
            "department": department,
            "status": "failed",
            "reason": "baseline_not_found",
        }

    if not device:
        return {
            "workflow": "posture_management",
            "hostname": hostname,
            "department": department,
            "status": "device_not_found",
        }

    findings = []

    os_name = _safe_get_os(device)
    encryption_enabled = device.get("fde", {}).get("active") is True
    policy_bound = device.get("isPolicyBound") is True

    if baseline["required_os"].lower() not in os_name.lower():
        findings.append("Operating system does not match baseline")

    if baseline["disk_encryption_required"] and not encryption_enabled:
        findings.append("Disk encryption is not enabled")

    if baseline["policy_required"] and not policy_bound:
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

    if posture.get("status") in ["device_not_found", "failed"]:
        return posture

    if posture.get("status") == "compliant":
        result = {
            "workflow": "posture_remediation",
            "hostname": hostname,
            "department": department,
            "posture_status": "compliant",
            "remediation_actions": [],
            "status": "no_action_required",
        }

        write_audit("posture_remediation", "no_action_required", result)
        return result

    findings = posture.get("findings", [])

    if "Disk encryption is not enabled" in findings:
        remediation_actions.append(
            apply_policy_real(
                policy_name=baseline["disk_encryption_policy_name"],
                target_group=baseline["target_group"],
                policy_type=baseline["policy_type"],
            )
        )

    if "Device is not policy bound" in findings:
        remediation_actions.append(
            apply_policy_real(
                policy_name=baseline["security_policy_name"],
                target_group=baseline["target_group"],
                policy_type=baseline["policy_type"],
            )
        )

    remediation_actions.append(
        run_command(
            command_name=baseline["remediation_commands"]["patching"],
            target_group=baseline["target_group"],
            script_type="powershell",
        )
    )

    result = {
        "workflow": "posture_remediation",
        "hostname": hostname,
        "department": department,
        "posture_status": posture.get("status"),
        "findings": findings,
        "remediation_actions": remediation_actions,
        "status": "completed",
    }

    write_audit("posture_remediation", "completed", result)
    return result