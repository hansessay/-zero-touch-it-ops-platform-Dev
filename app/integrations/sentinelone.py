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
        "message": (
            "Set SENTINELONE_BASE_URL and SENTINELONE_API_TOKEN "
            "in .env to enable real SentinelOne API calls."
        ),
    }

    write_audit(f"sentinelone_{action}", "skipped", result)
    return result


def _request(method, endpoint, action, params=None, json=None):
    base_url = _base_url()
    headers = _headers()

    if not base_url or not headers:
        return _not_configured(action)

    try:
        response = requests.request(
            method=method,
            url=f"{base_url}{endpoint}",
            headers=headers,
            params=params,
            json=json,
            timeout=30,
        )

        result = {
            "system": "SentinelOne",
            "action": action,
            "status": "completed" if response.ok else "failed",
            "status_code": response.status_code,
            "response": _parse_response(response),
        }

        write_audit(f"sentinelone_{action}", result["status"], result)
        return result

    except requests.exceptions.RequestException as e:
        result = {
            "system": "SentinelOne",
            "action": action,
            "status": "error",
            "message": str(e),
        }

        write_audit(f"sentinelone_{action}", "error", result)
        return result


def get_agents(limit: int = 50):
    return _request(
        method="GET",
        endpoint="/agents",
        action="get_agents",
        params={"limit": limit},
    )


def get_threats(limit: int = 50):
    return _request(
        method="GET",
        endpoint="/threats",
        action="get_threats",
        params={"limit": limit},
    )


def get_activities(limit: int = 50):
    return _request(
        method="GET",
        endpoint="/activities",
        action="get_activities",
        params={"limit": limit},
    )


def isolate_endpoint(agent_id: str):
    return _request(
        method="POST",
        endpoint="/agents/actions/disconnect",
        action="isolate_endpoint",
        json={
            "filter": {
                "ids": [agent_id],
            }
        },
    )


def check_agent_status(hostname: str):
    agents = get_agents(limit=100)

    result = {
        "system": "SentinelOne",
        "action": "check_agent_status",
        "hostname": hostname,
        "status": "completed",
        "message": (
            "Agent inventory lookup executed. Review the SentinelOne "
            "response and match hostname to agent_id."
        ),
        "agents": agents,
    }

    write_audit("sentinelone_check_agent_status", "completed", result)
    return result


def isolate_device(hostname: str):
    result = {
        "system": "SentinelOne",
        "action": "isolate_device",
        "hostname": hostname,
        "status": "requires_agent_id",
        "message": (
            "Safe guardrail applied. Hostname isolation requires mapping "
            "the hostname to a SentinelOne agent_id first. Then call "
            "isolate_endpoint(agent_id)."
        ),
    }

    write_audit("sentinelone_isolate_device", "requires_approval", result)
    return result


def endpoint_protection_summary():
    agents = get_agents()
    threats = get_threats()
    activities = get_activities()

    result = {
        "workflow": "sentinelone_endpoint_protection_summary",
        "status": "completed",
        "summary": {
            "agent_inventory_checked": True,
            "threats_checked": True,
            "activities_checked": True,
            "mode": "live_api" if os.getenv("SENTINELONE_API_TOKEN") else "not_configured",
        },
        "agents": agents,
        "threats": threats,
        "activities": activities,
    }

    write_audit(
        "sentinelone_endpoint_protection_summary",
        "completed",
        result,
    )

    return result