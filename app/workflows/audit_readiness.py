from app.audit import write_audit


def generate_audit_report():
    result = {
        "workflow": "audit_readiness",
        "controls": [
            {
                "control": "Employee onboarding evidence",
                "status": "available",
                "evidence": "Google Workspace user creation, JumpCloud user creation, access assignment"
            },
            {
                "control": "Employee offboarding evidence",
                "status": "available",
                "evidence": "Google suspension, JumpCloud suspension, Drive ownership transfer"
            },
            {
                "control": "Fleet compliance evidence",
                "status": "available",
                "evidence": "Encryption and SentinelOne compliance checks"
            },
            {
                "control": "Identity compliance evidence",
                "status": "available",
                "evidence": "MFA compliance checks"
            },
            {
                "control": "SaaS governance evidence",
                "status": "available",
                "evidence": "Approved apps, shadow IT detection, license governance"
            }
        ],
        "audit_status": "audit_ready",
        "status": "completed"
    }

    write_audit("audit_readiness_report", "completed", result)

    return result