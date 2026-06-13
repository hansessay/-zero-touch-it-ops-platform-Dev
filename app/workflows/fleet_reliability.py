from app.audit import write_audit
from app.integrations.jumpcloud import (
    get_devices,
    run_command,
    apply_policy_real,
)


PATCH_POLICIES = {
    "Engineering": {
        "policy_name": "JC Standard Security - Allow The Use of Biometrics",
        "target_group": "Engineering",
        "policy_type": "windows",
    }
}


def check_patch_status():
    devices_response = get_devices()
    devices = devices_response.get("response", {}).get("results", [])

    device_reports = []

    for device in devices:
        hostname = device.get("hostname") or device.get("displayName")
        os_name = device.get("os")
        os_version = device.get("version")
        last_contact = device.get("lastContact")
        active = device.get("active")

        device_reports.append({
            "hostname": hostname,
            "os": os_name,
            "os_version": os_version,
            "last_contact": last_contact,
            "active": active,
            "patch_status": "requires_validation",
        })

    result = {
        "workflow": "patch_compliance",
        "total_devices": len(device_reports),
        "devices": device_reports,
        "status": "completed",
    }

    write_audit("patch_compliance", "completed", result)
    return result


def run_patch_lifecycle(hostname: str, department: str = "Engineering"):
    policy = PATCH_POLICIES.get(department)

    if not policy:
        return {
            "workflow": "automated_patching",
            "hostname": hostname,
            "department": department,
            "status": "failed",
            "reason": "no_patch_policy_for_department",
        }

    actions = []

    policy_result = apply_policy_real(
        policy_name=policy["policy_name"],
        target_group=policy["target_group"],
        policy_type=policy["policy_type"],
    )
    actions.append(policy_result)

    command_result = run_command(
        command_name="Check Windows Update Status",
        target_group=policy["target_group"],
        script_type="powershell",
    )
    actions.append(command_result)

    result = {
        "workflow": "automated_patching",
        "hostname": hostname,
        "department": department,
        "actions": actions,
        "status": "completed",
    }

    write_audit("automated_patching", "completed", result)
    return result


def desired_state_check():
    patch_status = check_patch_status()

    drifted_devices = []

    for device in patch_status.get("devices", []):
        if not device.get("active"):
            drifted_devices.append({
                "hostname": device.get("hostname"),
                "reason": "device_not_active",
            })

    result = {
        "workflow": "desired_state",
        "baseline": "security_standard",
        "devices_checked": patch_status.get("total_devices"),
        "drift_detected": len(drifted_devices) > 0,
        "drifted_devices": drifted_devices,
        "status": "completed",
    }

    write_audit("desired_state_check", "completed", result)
    return result


def generate_audit_evidence():
    patch_status = check_patch_status()
    desired_state = desired_state_check()

    result = {
        "workflow": "audit_readiness",
        "framework": "SOC2",
        "evidence": {
            "patch_status": patch_status,
            "desired_state": desired_state,
            "evidence_sources": [
                "jumpcloud_devices",
                "patch_compliance_logs",
                "desired_state_checks",
                "workflow_audit_logs",
            ],
        },
        "status": "completed",
    }

    write_audit("audit_evidence", "completed", result)
    return result