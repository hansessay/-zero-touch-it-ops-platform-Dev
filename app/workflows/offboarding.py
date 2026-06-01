from app.integrations.jumpcloud import suspend_user
from app.integrations.google_workspace import suspend_google_user, transfer_drive_ownership
from app.audit import write_audit


def run_offboarding(email: str, manager_email: str, reason: str, transfer_owner: str | None):
    steps = []

    steps.append(suspend_user(email))
    steps.append(suspend_google_user(email))

    if transfer_owner:
        steps.append(transfer_drive_ownership(email, transfer_owner))

    result = {
        "workflow": "offboarding",
        "email": email,
        "manager_email": manager_email,
        "reason": reason,
        "status": "completed",
        "steps": steps
    }

    write_audit("offboarding_workflow", "completed", result)
    return result