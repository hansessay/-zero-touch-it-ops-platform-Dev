from app.audit import write_audit
from app.config import load_access_profiles
from app.integrations.google_workspace import add_user_to_group
from app.integrations.jumpcloud import apply_policy


def assign_department_access(user_email: str, department: str):
    config = load_access_profiles()
    departments = config.get("departments", {})

    access_profile = departments.get(department)

    if not access_profile:
        result = {
            "workflow": "access_management",
            "user_email": user_email,
            "department": department,
            "status": "failed",
            "reason": "department_access_profile_not_found"
        }

        write_audit("access_management", "failed", result)
        return result

    google_group_result = add_user_to_group(
        user_email=user_email,
        group_email=access_profile["google_group"]
    )

    jumpcloud_policy_result = apply_policy(
        policy_name=access_profile["jumpcloud_policy"],
        target_group=department,
        policy_type=access_profile["policy_type"]
    )

    result = {
        "workflow": "access_management",
        "user_email": user_email,
        "department": department,
        "google_group": google_group_result,
        "jumpcloud_policy": jumpcloud_policy_result,
        "status": "completed"
    }

    write_audit("access_management", "completed", result)

    return result