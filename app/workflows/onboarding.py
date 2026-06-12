from app.audit import write_audit
from app.workflows.rbac import evaluate_rbac
from app.integrations.google_workspace import create_google_user
from app.integrations.jumpcloud import (
    create_jumpcloud_user,
    add_user_to_group_by_id,
    apply_policy_real,
)
from app.workflows.access_management import assign_department_access
from app.database import save_workflow_run


ENGINEERING_USER_GROUP_ID = "6a2c556ab583270001eb67d3"
ENGINEERING_POLICY_NAME = "JC Standard Security - Allow The Use of Biometrics"


def run_onboarding(employee):
    try:
        google_result = create_google_user(
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.employee_email,
            department=employee.department,
        )
    except Exception as error:
        google_result = {
            "system": "Google Workspace",
            "status": "failed",
            "error": str(error),
        }

    try:
        jumpcloud_result = create_jumpcloud_user(
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.employee_email,
            department=employee.department,
        )
    except Exception as error:
        jumpcloud_result = {
            "system": "JumpCloud",
            "status": "failed",
            "error": str(error),
        }

    jumpcloud_group_result = {
        "system": "JumpCloud",
        "action": "add_user_to_group",
        "status": "skipped",
    }

    jumpcloud_policy_result = {
        "system": "JumpCloud",
        "action": "apply_policy",
        "status": "skipped",
    }

    try:
        if jumpcloud_result.get("status") == "success":
            jumpcloud_user_id = (
                jumpcloud_result
                .get("response", {})
                .get("id")
            )

            if employee.department == "Engineering" and jumpcloud_user_id:
                jumpcloud_group_result = add_user_to_group_by_id(
                    user_id=jumpcloud_user_id,
                    user_group_id=ENGINEERING_USER_GROUP_ID,
                )

                jumpcloud_policy_result = apply_policy_real(
                    policy_name=ENGINEERING_POLICY_NAME,
                    target_group="Engineering",
                    policy_type="windows",
                )

    except Exception as error:
        jumpcloud_group_result = {
            "system": "JumpCloud",
            "action": "group_assignment",
            "status": "failed",
            "error": str(error),
        }

        jumpcloud_policy_result = {
            "system": "JumpCloud",
            "action": "policy_assignment",
            "status": "failed",
            "error": str(error),
        }

    access_result = assign_department_access(
        user_email=employee.employee_email,
        department=employee.department,
    )

    rbac_result = evaluate_rbac(
        user_email=employee.employee_email,
        department=employee.department,
        job_title=employee.job_title,
    )

    result = {
        "workflow": "onboarding",
        "google_workspace": google_result,
        "jumpcloud": jumpcloud_result,
        "jumpcloud_group_assignment": jumpcloud_group_result,
        "jumpcloud_policy_assignment": jumpcloud_policy_result,
        "access_management": access_result,
        "rbac": rbac_result,
        "status": "completed",
    }

    write_audit(
        "onboarding_workflow",
        "completed",
        result,
    )

    save_workflow_run(
        workflow="onboarding",
        employee_email=employee.employee_email,
        status=result["status"],
        result=result,
    )

    return result