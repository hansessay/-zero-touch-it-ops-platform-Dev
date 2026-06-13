from app.audit import write_audit
from app.integrations.google_workspace.admin_client import list_oauth_token_events


APPROVED_APPS = [
    "Google Chrome",
    "JumpCloud",
    "GAM",
    "Google Workspace",
    "Slack",
    "GitHub",
    "Jira",
    "Confluence",
    "SentinelOne",
]


def _get_parameter(parameters, name):
    for parameter in parameters:
        if parameter.get("name") == name:
            return parameter.get("value") or parameter.get("multiValue")
    return None


def _extract_oauth_apps(events):
    discovered_apps = []

    for item in events:
        actor = item.get("actor", {}).get("email")
        ip_address = item.get("ipAddress")
        event_time = item.get("id", {}).get("time")

        for event in item.get("events", []):
            parameters = event.get("parameters", [])

            app_name = _get_parameter(parameters, "app_name")
            client_id = _get_parameter(parameters, "client_id")
            scopes = _get_parameter(parameters, "scope") or []

            if not app_name:
                continue

            discovered_apps.append({
                "name": app_name,
                "client_id": client_id,
                "actor": actor,
                "ip_address": ip_address,
                "event_time": event_time,
                "scopes": scopes,
                "approved": app_name in APPROVED_APPS,
                "source": "google_workspace_token_audit",
            })

    return discovered_apps


def discover_saas_apps():
    oauth_events = list_oauth_token_events(max_results=100)
    discovered_apps = _extract_oauth_apps(oauth_events)

    approved = []
    shadow_it = []

    for app in discovered_apps:
        if app["approved"]:
            approved.append(app)
        else:
            shadow_it.append(app)

    result = {
        "workflow": "saas_discovery",
        "source": "google_workspace_token_audit",
        "total_events": len(oauth_events),
        "total_apps": len(discovered_apps),
        "approved_count": len(approved),
        "shadow_it_count": len(shadow_it),
        "approved_apps": approved,
        "shadow_it_apps": shadow_it,
        "status": "completed",
    }

    write_audit("saas_discovery", "completed", result)
    return result


def license_governance():
    discovery = discover_saas_apps()

    result = {
        "workflow": "license_governance",
        "source": "google_workspace_token_audit",
        "shadow_it_count": discovery["shadow_it_count"],
        "shadow_it_apps": discovery["shadow_it_apps"],
        "note": "License waste requires SaaS license APIs or expense data. OAuth logs identify app usage, not license counts.",
        "status": "completed",
    }

    write_audit("license_governance", "completed", result)
    return result