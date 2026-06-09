from datetime import datetime
from app.audit import write_audit

APPROVALS = []


def create_approval_request(workflow: str, employee_email: str, requested_by: str = "system"):
    approval = {
        "id": len(APPROVALS) + 1,
        "workflow": workflow,
        "employee_email": employee_email,
        "status": "pending_approval",
        "requested_by": requested_by,
        "approved_by": None,
        "created_at": datetime.utcnow().isoformat(),
    }

    APPROVALS.append(approval)
    write_audit("approval_requested", "pending", approval)
    return approval


def list_approvals():
    return APPROVALS


def approve_request(approval_id: int, approved_by: str = "manager"):
    for approval in APPROVALS:
        if approval["id"] == approval_id:
            approval["status"] = "approved"
            approval["approved_by"] = approved_by
            write_audit("approval_approved", "completed", approval)
            return approval

    raise ValueError("Approval request not found")


def reject_request(approval_id: int, rejected_by: str = "manager"):
    for approval in APPROVALS:
        if approval["id"] == approval_id:
            approval["status"] = "rejected"
            approval["approved_by"] = rejected_by
            write_audit("approval_rejected", "completed", approval)
            return approval

    raise ValueError("Approval request not found")