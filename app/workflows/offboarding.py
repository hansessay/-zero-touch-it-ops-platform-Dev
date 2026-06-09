from app.audit import write_audit
from app.database import save_workflow_run
from app.integrations.google_workspace import (
    suspend_google_user,
    remove_user_from_all_groups,
)
from app.integrations.jumpcloud import suspend_user


def run_offboarding(employee):
    try:
        google_groups_result = remove_user_from_all_groups(
            employee.employee_email
        )
    except Exception as error:
        google_groups_result = {
            "system": "Google Workspace",
            "action": "remove_user_from_all_groups",
            "status": "failed",
            "error": str(error),
        }

    try:
        google_result = suspend_google_user(
            employee.employee_email
        )
    except Exception as error:
        google_result = {
            "system": "Google Workspace",
            "action": "suspend_user",
            "status": "failed",
            "error": str(error),
        }

    try:
        jumpcloud_result = suspend_user(
            employee.employee_email
        )
    except Exception as error:
        jumpcloud_result = {
            "system": "JumpCloud",
            "action": "suspend_user",
            "status": "failed",
            "error": str(error),
        }

    overall_status = "completed"

    if (
        google_groups_result.get("status") == "failed"
        or google_result.get("status") == "failed"
        or jumpcloud_result.get("status") in ["failed", "user_not_found"]
    ):
        overall_status = "completed_with_errors"

    result = {
        "workflow": "offboarding",
        "employee_email": employee.employee_email,
        "manager_email": employee.manager_email,
        "reason": employee.reason,
        "transfer_ownership_to": employee.transfer_ownership_to,
        "google_group_removal": google_groups_result,
        "google_workspace": google_result,
        "jumpcloud": jumpcloud_result,
        "actions": [
            "Remove Google group memberships",
            "Suspend Google Workspace account",
            "Suspend JumpCloud account",
            "Revoke SaaS access",
            "Transfer ownership",
            "Write audit log",
        ],
        "status": overall_status,
    }

    write_audit(
        "offboarding_workflow",
        overall_status,
        result,
    )

    save_workflow_run(
        workflow="offboarding",
        employee_email=employee.employee_email,
        status=result["status"],
        result=result,
    )

    return result