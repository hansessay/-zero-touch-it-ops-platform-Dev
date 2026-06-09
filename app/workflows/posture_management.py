from app.audit import write_audit
from app.integrations.jumpcloud import run_command


DESIRED_STATE = {
    "bitlocker_enabled": True,
    "sentinelone_installed": True,
    "firewall_enabled": True,
    "screen_lock_enabled": True,
    "os_supported": True,
}


def get_desired_state():
    result = {
        "workflow": "desired_state_baseline",
        "desired_state": DESIRED_STATE,
        "status": "completed",
    }

    write_audit("desired_state_baseline", "completed", result)
    return result


def check_device_posture(hostname: str):
    # Simulated device state for demo
    current_state = {
        "bitlocker_enabled": True,
        "sentinelone_installed": True,
        "firewall_enabled": True,
        "screen_lock_enabled": True,
        "os_supported": True,
    }

    drift = {}

    for control, expected_value in DESIRED_STATE.items():
        actual_value = current_state.get(control)

        if actual_value != expected_value:
            drift[control] = {
                "expected": expected_value,
                "actual": actual_value,
            }

    compliant = len(drift) == 0
    score = int(
        ((len(DESIRED_STATE) - len(drift)) / len(DESIRED_STATE)) * 100
    )

    result = {
        "workflow": "check_device_posture",
        "hostname": hostname,
        "desired_state": DESIRED_STATE,
        "current_state": current_state,
        "drift": drift,
        "compliant": compliant,
        "compliance_score": score,
        "status": "completed",
    }

    write_audit("check_device_posture", "completed", result)
    return result


def remediate_device_posture(hostname: str):
    posture = check_device_posture(hostname)
    drift = posture["drift"]

    remediation_actions = []

    if not drift:
        result = {
            "workflow": "remediate_device_posture",
            "hostname": hostname,
            "message": "Device is already compliant. No remediation required.",
            "status": "completed",
        }

        write_audit("remediate_device_posture", "completed", result)
        return result

    for control in drift.keys():
        if control == "firewall_enabled":
            remediation_actions.append(
                run_command(
                    command_name="Enable Windows Firewall",
                    target_group=hostname,
                    script_type="powershell",
                )
            )

        elif control == "bitlocker_enabled":
            remediation_actions.append(
                run_command(
                    command_name="Enable BitLocker",
                    target_group=hostname,
                    script_type="powershell",
                )
            )

        elif control == "screen_lock_enabled":
            remediation_actions.append(
                run_command(
                    command_name="Enforce Screen Lock Policy",
                    target_group=hostname,
                    script_type="powershell",
                )
            )

        elif control == "sentinelone_installed":
            remediation_actions.append(
                {
                    "system": "SentinelOne",
                    "action": "install_agent",
                    "hostname": hostname,
                    "status": "manual_review_required",
                }
            )

        else:
            remediation_actions.append(
                {
                    "control": control,
                    "status": "manual_review_required",
                }
            )

    result = {
        "workflow": "remediate_device_posture",
        "hostname": hostname,
        "drift_detected": drift,
        "remediation_actions": remediation_actions,
        "status": "completed",
    }

    write_audit("remediate_device_posture", "completed", result)
    return result