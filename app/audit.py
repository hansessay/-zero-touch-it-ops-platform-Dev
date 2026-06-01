from datetime import datetime

audit_log = []


def write_audit(action: str, status: str, details: dict):
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "status": status,
        "details": details
    }
    audit_log.append(event)
    return event


def get_audit_log():
    return audit_log