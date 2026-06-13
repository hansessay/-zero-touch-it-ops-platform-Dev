from app.audit import write_audit
from app.integrations.jumpcloud import get_devices
from app.integrations.google_workspace import list_users
from app.workflows.saas_governance import discover_saas_apps


def _safe_percentage(part, total):
    if total == 0:
        return "0%"
    return f"{round((part / total) * 100, 2)}%"


def get_fleet_telemetry():
    devices_response = get_devices()
    devices = devices_response.get("response", {}).get("results", [])

    users = list_users(max_results=100)

    saas = discover_saas_apps()

    total_devices = len(devices)
    active_devices = len([
        device for device in devices
        if device.get("active") is True
    ])

    encrypted_devices = len([
        device for device in devices
        if device.get("fde", {}).get("active") is True
    ])

    policy_bound_devices = len([
        device for device in devices
        if device.get("isPolicyBound") is True
    ])

    at_risk_devices = total_devices - active_devices

    telemetry = {
        "workflow": "observability_telemetry",
        "fleet_health": {
            "total_devices": total_devices,
            "active_devices": active_devices,
            "at_risk_devices": at_risk_devices,
            "encrypted_devices": encrypted_devices,
            "policy_bound_devices": policy_bound_devices,
            "encryption_coverage": _safe_percentage(
                encrypted_devices,
                total_devices,
            ),
            "policy_coverage": _safe_percentage(
                policy_bound_devices,
                total_devices,
            ),
        },
        "identity_health": {
            "google_workspace_users": len(users),
        },
        "saas_governance": {
            "total_oauth_events": saas.get("total_events"),
            "total_discovered_apps": saas.get("total_apps"),
            "approved_apps": saas.get("approved_count"),
            "shadow_it_apps": saas.get("shadow_it_count"),
        },
        "leadership_summary": [
            f"{total_devices} JumpCloud devices discovered",
            f"{len(users)} Google Workspace users discovered",
            f"{saas.get('shadow_it_count')} unauthorized OAuth app events detected",
            "Telemetry generated from live JumpCloud and Google Workspace APIs",
        ],
        "status": "completed",
    }

    write_audit(
        "observability_telemetry",
        "completed",
        telemetry,
    )

    return telemetry