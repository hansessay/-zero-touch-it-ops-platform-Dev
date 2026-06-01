from app.audit import write_audit


def suspend_user(email: str):
    result = {
        "system": "JumpCloud",
        "action": "suspend_user",
        "email": email,
        "status": "simulated_success"
    }
    write_audit("jumpcloud_suspend_user", "success", result)
    return result


def run_command(command_name: str, target_group: str, script_type: str):
    result = {
        "system": "JumpCloud",
        "action": "run_command",
        "command_name": command_name,
        "target_group": target_group,
        "script_type": script_type,
        "status": "simulated_success"
    }
    write_audit("jumpcloud_run_command", "success", result)
    return result


def apply_policy(policy_name: str, target_group: str, policy_type: str):
    result = {
        "system": "JumpCloud",
        "action": "apply_policy",
        "policy_name": policy_name,
        "target_group": target_group,
        "policy_type": policy_type,
        "status": "simulated_success"
    }
    write_audit("jumpcloud_apply_policy", "success", result)
    return result