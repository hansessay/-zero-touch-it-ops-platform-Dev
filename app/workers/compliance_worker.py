import time

from app.audit import write_audit
from app.integrations.jumpcloud import get_devices, apply_policy_real

try:
    from app.integrations.sentinelone import check_agent_status
except ImportError:
    def check_agent_status(hostname):
        return {
            "system": "SentinelOne",
            "hostname": hostname,
            "status": "unknown",
            "reason": "check_agent_status_not_implemented",
        }


CHECK_INTERVAL_SECONDS = 3600

BASELINE_BY_DEPARTMENT = {
    "Engineering": {
        "disk_encryption": True,
        "sentinelone_required": True,
        "patch_policy": "JC Standard Security - Allow The Use of Biometrics",
    }
}


def get_department_for_device(device: dict) -> str:
    return "Engineering"


def check_device_compliance(device: dict):
    hostname = device.get("hostname") or device.get("displayName")
    department = get_department_for_device(device)
    baseline = BASELINE_BY_DEPARTMENT.get(department, {})

    findings = []
    remediation_actions = []

    sentinelone_status = check_agent_status(hostname)

    if baseline.get("sentinelone_required"):
        if sentinelone_status.get("status") != "protected":
            findings.append("SentinelOne agent not protected")

    disk_encryption_enabled = device.get("fde", {}).get("active") is True

    if baseline.get("disk_encryption") and not disk_encryption_enabled:
        findings.append("Disk encryption is disabled")

    if baseline.get("patch_policy"):
        remediation = apply_policy_real(
            policy_name=baseline["patch_policy"],
            target_group=department,
            policy_type="windows",
        )
        remediation_actions.append(remediation)

    status = "compliant" if not findings else "drift_detected"

    result = {
        "workflow": "compliance_worker",
        "hostname": hostname,
        "department": department,
        "status": status,
        "findings": findings,
        "sentinelone_status": sentinelone_status,
        "remediation_actions": remediation_actions,
    }

    write_audit("compliance_worker", status, result)
    return result


def run_compliance_worker():
    print("Compliance worker started")

    while True:
        devices_response = get_devices()
        devices = devices_response.get("response", {}).get("results", [])

        for device in devices:
            result = check_device_compliance(device)
            print(result)

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_compliance_worker()