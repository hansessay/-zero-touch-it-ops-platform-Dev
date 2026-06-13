# Writes an audit event so every workflow action is traceable
from app.audit import write_audit

# Evaluates role-based access control based on department and job title
from app.workflows.rbac import evaluate_rbac

# Creates the employee account in Google Workspace
from app.integrations.google_workspace import create_google_user

# Creates the employee account in JumpCloud
from app.integrations.jumpcloud import create_jumpcloud_user

# Assigns department-based access such as groups, apps, or permissions
from app.workflows.access_management import assign_department_access

# Saves the workflow execution result into the database
from app.database import save_workflow_run


def run_onboarding(employee):
    """
    Main onboarding workflow.

    This function receives an employee object from FastAPI,
    provisions the user in Google Workspace and JumpCloud,
    assigns access, evaluates RBAC rules, writes audit evidence,
    saves workflow history, and returns a structured result.
    """

    # Step 1: Try to create the user in Google Workspace.
    # If the API call fails, capture the error instead of stopping the full workflow.
    try:
        google_result = create_google_user(
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.employee_email,
            department=employee.department,
        )

    # If Google Workspace provisioning fails, return a controlled failure object.
    except Exception as error:
        google_result = {
            "system": "Google Workspace",
            "status": "failed",
            "error": str(error),
        }

    # Step 2: Try to create the user in JumpCloud.
    # JumpCloud is used for identity, device, and endpoint management.
    try:
        jumpcloud_result = create_jumpcloud_user(
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.employee_email,
            department=employee.department,
        )

    # If JumpCloud provisioning fails, capture the error without crashing the workflow.
    except Exception as error:
        jumpcloud_result = {
            "system": "JumpCloud",
            "status": "failed",
            "error": str(error),
        }

    # Step 3: Assign access based on the employee's department.
    # Example: Engineering users may receive engineering groups or tools.
    access_result = assign_department_access(
        user_email=employee.employee_email,
        department=employee.department,
    )

    # Step 4: Evaluate RBAC rules.
    # This checks what access the user should receive based on department and job title.
    rbac_result = evaluate_rbac(
        user_email=employee.employee_email,
        department=employee.department,
        job_title=employee.job_title,
    )

    # Step 5: Build one structured response containing all onboarding results.
    # This makes the API response easy to inspect from Streamlit, Swagger, or logs.
    result = {
        "workflow": "onboarding",
        "google_workspace": google_result,
        "jumpcloud": jumpcloud_result,
        "access_management": access_result,
        "rbac": rbac_result,
        "status": "completed",
    }

    # Step 6: Write an audit record for compliance and troubleshooting.
    write_audit(
        "onboarding_workflow",
        "completed",
        result,
    )

    # Step 7: Save workflow history in the database.
    # This supports /workflows/history and gives visibility into previous runs.
    save_workflow_run(
        workflow="onboarding",
        employee_email=employee.employee_email,
        status=result["status"],
        result=result,
    )

    # Step 8: Return the final onboarding result to FastAPI,
    # which sends it back to the Streamlit UI or API client.
    return result