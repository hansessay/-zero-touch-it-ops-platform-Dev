from app.audit import write_audit


def run_onboarding(
    full_name,
    email,
    department,
    role,
    manager_email
):

    result = {
        "workflow": "onboarding",
        "full_name": full_name,
        "email": email,
        "department": department,
        "role": role,
        "manager_email": manager_email,
        "status": "completed"
    }

    write_audit(
        "onboarding_workflow",
        "completed",
        result
    )

    return result