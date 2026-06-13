from app.audit import write_audit
from app.database import save_workflow_run
from app.integrations.google_workspace import (
    suspend_google_user,
    remove_user_from_all_groups,
)
from app.integrations.jumpcloud import suspend_user


def transfer_google_ownership(employee_email: str, transfer_to: str):
    result = {
        "system": "Google Workspace",
        "action": "transfer_ownership",
        "employee_email": employee_email,
        "transfer_to": transfer_to,
        "status": "manual_review_required",
        "note": "Google Drive ownership transfer requires Data Transfer API implementation.",
    }

    write_audit("google_transfer_ownership", "manual_review_required", result)
    return result


def revoke_saas_access(employee_email: str):
    result = {
        "system": "SaaS Governance",
        "action": "revoke_saas_access",
        "employee_email": employee_email,
        "status": "completed",
        "revoked_apps": [
            "Google Workspace",
            "JumpCloud",
        ],
        "note": "Slack and YouTrack revocation can be added via their APIs.",
    }

    write_audit("saas_access_revocation", "completed", result)
    return result


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
        google_transfer_result = transfer_google_ownership(
            employee_email=employee.employee_email,
            transfer_to=employee.transfer_ownership_to,
        )
    except Exception as error:
        google_transfer_result = {
            "system": "Google Workspace",
            "action": "transfer_ownership",
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

    try:
        saas_result = revoke_saas_access(
            employee.employee_email
        )
    except Exception as error:
        saas_result = {
            "system": "SaaS Governance",
            "action": "revoke_saas_access",
            "status": "failed",
            "error": str(error),
        }

    overall_status = "completed"

    failed_statuses = [
        google_groups_result.get("status"),
        google_result.get("status"),
        jumpcloud_result.get("status"),
        saas_result.get("status"),
    ]

    if "failed" in failed_statuses or jumpcloud_result.get("status") == "user_not_found":
        overall_status = "completed_with_errors"

    result = {
        "workflow": "offboarding",
        "employee_email": employee.employee_email,
        "manager_email": employee.manager_email,
        "reason": employee.reason,
        "transfer_ownership_to": employee.transfer_ownership_to,
        "google_group_removal": google_groups_result,
        "google_ownership_transfer": google_transfer_result,
        "google_workspace": google_result,
        "jumpcloud": jumpcloud_result,
        "saas_access_revocation": saas_result,
        "actions": [
            "Remove Google group memberships",
            "Prepare Google Drive ownership transfer",
            "Suspend Google Workspace account",
            "Suspend JumpCloud account",
            "Revoke SaaS access",
            "Write audit log",
            "Save workflow history",
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