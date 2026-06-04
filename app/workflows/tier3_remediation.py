from app.audit import write_audit
from app.integrations.jumpcloud import run_command, apply_policy


def remediate_device(hostname: str, issue: str):

    command_result = run_command(
        command_name=f"remediate_{issue}",
        target_group=hostname,
        script_type="powershell"
    )

    policy_result = apply_policy(
        policy_name=f"{issue}_policy",
        target_group=hostname,
        policy_type="security"
    )

    result = {
        "workflow": "tier3_remediation",
        "hostname": hostname,
        "issue": issue,
        "command": command_result,
        "policy": policy_result,
        "status": "completed"
    }

    write_audit(
        "tier3_remediation",
        "completed",
        result
    )

    return result