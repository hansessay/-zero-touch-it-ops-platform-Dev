from datetime import datetime
import json

audit_log = []


def write_audit(action: str, status: str, details: dict):
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "status": status,
        "details": details
    }

    audit_log.append(event)

    with open("audit.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

    return event


def get_audit_log():
    return audit_log