from app.audit import write_audit


def get_agents():
    result = {
        "system": "SentinelOne",
        "action": "get_agents",
        "status": "api_ready_placeholder",
        "message": "SentinelOne agent inventory placeholder"
    }

    write_audit("sentinelone_get_agents", "completed", result)
    return result


def check_agent_status(hostname: str):
    result = {
        "system": "SentinelOne",
        "action": "check_agent_status",
        "hostname": hostname,
        "status": "protected_placeholder",
        "agent_health": "online",
        "threat_status": "clean"
    }

    write_audit("sentinelone_check_agent_status", "completed", result)
    return result


def isolate_device(hostname: str):
    result = {
        "system": "SentinelOne",
        "action": "isolate_device",
        "hostname": hostname,
        "status": "api_ready_placeholder",
        "message": "Device isolation would be triggered through SentinelOne API"
    }

    write_audit("sentinelone_isolate_device", "completed", result)
    return result