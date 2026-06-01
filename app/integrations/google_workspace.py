from app.audit import write_audit


def suspend_google_user(email: str):
    result = {
        "system": "Google Workspace",
        "action": "suspend_user",
        "email": email,
        "status": "simulated_success"
    }
    write_audit("google_suspend_user", "success", result)
    return result


def add_user_to_group(user_email: str, group_email: str):
    result = {
        "system": "Google Workspace",
        "action": "add_user_to_group",
        "user_email": user_email,
        "group_email": group_email,
        "status": "simulated_success"
    }
    write_audit("google_add_user_to_group", "success", result)
    return result


def transfer_drive_ownership(old_owner: str, new_owner: str):
    result = {
        "system": "Google Workspace",
        "action": "transfer_drive_ownership",
        "old_owner": old_owner,
        "new_owner": new_owner,
        "status": "simulated_success"
    }
    write_audit("google_transfer_drive_ownership", "success", result)
    return result