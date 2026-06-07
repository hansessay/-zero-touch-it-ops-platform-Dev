from app.audit import write_audit
from app.workflows.rbac import evaluate_rbac
from app.integrations.google_workspace import create_google_user
from app.integrations.jumpcloud import create_jumpcloud_user
from app.workflows.access_management import assign_department_access


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

    # Department-based access assignment
    access_result = assign_department_access(
        user_email=employee.employee_email,
        department=employee.department,
    )

    # RBAC evaluation
    rbac_result = evaluate_rbac(
        user_email=employee.employee_email,
        department=employee.department,
        job_title=employee.job_title,
    )

    result = {
        "workflow": "onboarding",
        "google_workspace": google_result,
        "jumpcloud": jumpcloud_result,
        "access_management": access_result,
        "rbac": rbac_result,
        "status": "completed",
    }

    write_audit("onboarding_workflow", "completed", result)

    return result