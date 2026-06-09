import os
import requests

from app.audit import write_audit


def _base_url():
    url = os.getenv("SENTINELONE_BASE_URL")

    if not url:
        return None

    return url.rstrip("/") + "/web/api/v2.1"


def _headers():
    token = os.getenv("SENTINELONE_API_TOKEN")

    if not token:
        return None

    return {
        "Authorization": f"ApiToken {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _parse_response(response):
    try:
        return response.json()
    except Exception:
        return response.text


def _not_configured(action):
    result = {
        "system": "SentinelOne",
        "action": action,
        "status": "not_configured",
        "message": "Set SENTINELONE_BASE_URL and SENTINELONE_API_TOKEN in .env to enable real SentinelOne API calls.",
    }

    write_audit(f"sentinelone_{action}", "skipped", result)
    return result


def get_agents(limit: int = 50):
    base_url = _base_url()
    headers = _headers()

    if not base_url or not headers:
        return _not_configured("get_agents")

    response = requests.get(
        f"{base_url}/agents",
        headers=headers,
        params={"limit": limit},
        timeout=30,
    )

    result = {
        "system": "SentinelOne",
        "action": "get_agents",
        "status_code": response.status_code,
        "response": _parse_response(response),
    }

    write_audit("sentinelone_get_agents", "completed", result)
    return result


def get_threats(limit: int = 50):
    base_url = _base_url()
    headers = _headers()

    if not base_url or not headers:
        return _not_configured("get_threats")

    response = requests.get(
        f"{base_url}/threats",
        headers=headers,
        params={"limit": limit},
        timeout=30,
    )

    result = {
        "system": "SentinelOne",
        "action": "get_threats",
        "status_code": response.status_code,
        "response": _parse_response(response),
    }

    write_audit("sentinelone_get_threats", "completed", result)
    return result


def get_activities(limit: int = 50):
    base_url = _base_url()
    headers = _headers()

    if not base_url or not headers:
        return _not_configured("get_activities")

    response = requests.get(
        f"{base_url}/activities",
        headers=headers,
        params={"limit": limit},
        timeout=30,
    )

    result = {
        "system": "SentinelOne",
        "action": "get_activities",
        "status_code": response.status_code,
        "response": _parse_response(response),
    }

    write_audit("sentinelone_get_activities", "completed", result)
    return result


def isolate_endpoint(agent_id: str):
    base_url = _base_url()
    headers = _headers()

    if not base_url or not headers:
        return _not_configured("isolate_endpoint")

    response = requests.post(
        f"{base_url}/agents/actions/disconnect",
        headers=headers,
        json={
            "filter": {
                "ids": [agent_id]
            }
        },
        timeout=30,
    )

    result = {
        "system": "SentinelOne",
        "action": "isolate_endpoint",
        "agent_id": agent_id,
        "status_code": response.status_code,
        "response": _parse_response(response),
    }

    write_audit("sentinelone_isolate_endpoint", "completed", result)
    return result


def endpoint_protection_summary():
    agents = get_agents()
    threats = get_threats()

    result = {
        "workflow": "sentinelone_endpoint_protection_summary",
        "agents": agents,
        "threats": threats,
        "status": "completed",
    }

    write_audit(
        "sentinelone_endpoint_protection_summary",
        "completed",
        result
    )

    return result