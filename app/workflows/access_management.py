from app.audit import write_audit
from app.integrations.google_workspace import add_user_to_group
from app.integrations.jumpcloud import apply_policy


DEPARTMENT_ACCESS = {
    "IT": {
        "google_group": "it@company.com",
        "jumpcloud_policy": "IT Security Baseline",
        "policy_type": "security"
    },
    "Engineering": {
        "google_group": "engineering@company.com",
        "jumpcloud_policy": "Engineering Device Policy",
        "policy_type": "device"
    },
    "HR": {
        "google_group": "hr@company.com",
        "jumpcloud_policy": "HR Access Policy",
        "policy_type": "access"
    }
}


def assign_department_access(user_email: str, department: str):
    access_profile = DEPARTMENT_ACCESS.get(department)

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