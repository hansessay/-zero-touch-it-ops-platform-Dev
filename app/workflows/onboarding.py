from app.audit import write_audit
from app.integrations.google_directory import create_google_user
from app.integrations.jumpcloud import create_jumpcloud_user
from app.workflows.access_management import assign_department_access


def run_onboarding(employee):

    try:
        google_result = create_google_user(
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.employee_email,
            department=employee.department
        )
    except Exception as error:
        google_result = {
            "system": "Google Workspace",
            "status": "failed",
            "error": str(error)
        }

    try:
        jumpcloud_result = create_jumpcloud_user(
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.employee_email,
            department=employee.department
        )
    except Exception as error:
        jumpcloud_result = {
            "system": "JumpCloud",
            "status": "failed",
            "error": str(error)
        }

    access_result = assign_department_access(
        user_email=employee.employee_email,
        department=employee.department
    )

    result = {
        "workflow": "onboarding",
        "google_workspace": google_result,
        "jumpcloud": jumpcloud_result,
        "access_management": access_result,
        "status": "completed_with_errors"
    }

    write_audit("onboarding_workflow", "completed", result)

    return result