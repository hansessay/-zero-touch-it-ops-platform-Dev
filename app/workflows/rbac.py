from app.audit import write_audit

RBAC_RULES = {
    "IT": {
        "google_group": "it@cheikhops.com",
        "jumpcloud_group": "IT",
        "access_level": "admin_tools",
        "policies": ["IT Security Baseline", "BitLocker Full Disk Encryption"],
    },
    "Engineering": {
        "google_group": "engineering@cheikhops.com",
        "jumpcloud_group": "Engineering",
        "access_level": "developer_tools",
        "policies": ["Developer Security Baseline"],
    },
    "Finance": {
        "google_group": "finance@cheikhops.com",
        "jumpcloud_group": "Finance",
        "access_level": "finance_apps",
        "policies": ["Finance Security Baseline"],
    },
    "HR": {
        "google_group": "hr@cheikhops.com",
        "jumpcloud_group": "HR",
        "access_level": "hr_apps",
        "policies": ["HR Security Baseline"],
    },
}


def evaluate_rbac(user_email: str, department: str, job_title: str = ""):
    rule = RBAC_RULES.get(department)

    if not rule:
        result = {
            "system": "RBAC",
            "user_email": user_email,
            "department": department,
            "job_title": job_title,
            "status": "denied",
            "reason": "No RBAC rule exists for this department",
        }
        write_audit("rbac_evaluation", "completed", result)
        return result

    result = {
        "system": "RBAC",
        "user_email": user_email,
        "department": department,
        "job_title": job_title,
        "google_group": rule["google_group"],
        "jumpcloud_group": rule["jumpcloud_group"],
        "access_level": rule["access_level"],
        "policies": rule["policies"],
        "status": "approved",
    }

    write_audit("rbac_evaluation", "completed", result)
    return result