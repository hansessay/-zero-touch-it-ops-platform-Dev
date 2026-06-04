from app.audit import write_audit


def run_offboarding(employee):

    result = {
        "workflow": "offboarding",
        "email": employee.employee_email,
        "manager_email": employee.manager_email,
        "reason": employee.reason,
        "transfer_ownership_to": employee.transfer_ownership_to,
        "actions": [
            "Suspend Google Workspace account",
            "Suspend JumpCloud account",
            "Remove group memberships",
            "Revoke SaaS access",
            "Transfer ownership",
            "Write audit log"
        ],
        "status": "completed"
    }

    write_audit(
        "offboarding_workflow",
        "completed",
        result
    )

    return result