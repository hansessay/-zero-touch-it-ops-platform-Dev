import time
from app.audit import write_audit
from app.integrations.jumpcloud import apply_policy
from app.integrations.sentinelone import check_agent_status


CHECK_INTERVAL_SECONDS = 3600


DEVICES = [
    {
        "hostname": "LAPTOP-7UU6G70R",
        "department": "Engineering",
        "baseline": {
            "disk_encryption": True,
            "sentinelone_required": True,
            "patch_policy": "Standard Patch Policy",
        },
    }
]


def check_device_compliance(device: dict):
    hostname = device["hostname"]
    department = device["department"]
    baseline = device["baseline"]

    findings = []
    remediation_actions = []

    sentinelone_status = check_agent_status(hostname)

    if baseline["sentinelone_required"]:
        if sentinelone_status.get("status") != "protected":
            findings.append("SentinelOne agent not protected")

    disk_encryption_enabled = False

    if baseline["disk_encryption"] and not disk_encryption_enabled:
        findings.append("Disk encryption is disabled")

        remediation = apply_policy(
            policy_name="Disk Encryption Policy",
            target_group=department,
            policy_type="security",
        )

        remediation_actions.append(remediation)

    patch_remediation = apply_policy(
        policy_name=baseline["patch_policy"],
        target_group=department,
        policy_type="patching",
    )

    remediation_actions.append(patch_remediation)

    status = "compliant" if not findings else "drift_detected"

    result = {
        "workflow": "compliance_worker",
        "hostname": hostname,
        "department": department,
        "status": status,
        "findings": findings,
        "remediation_actions": remediation_actions,
    }

    write_audit("compliance_worker", status, result)

    return result


def run_compliance_worker():
    print("Compliance worker started")

    while True:
        for device in DEVICES:
            result = check_device_compliance(device)
            print(result)

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_compliance_worker()