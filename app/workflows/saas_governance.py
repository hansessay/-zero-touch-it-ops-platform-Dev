from app.audit import write_audit


APPROVED_APPS = [
    "Google Workspace",
    "JumpCloud",
    "Slack",
    "GitHub",
    "Jira",
    "Confluence",
    "SentinelOne"
]


DISCOVERED_APPS = [
    {
        "name": "Google Workspace",
        "owner": "IT",
        "license_count": 120,
        "monthly_cost": 850,
        "source": "admin_console"
    },
    {
        "name": "Slack",
        "owner": "IT",
        "license_count": 95,
        "monthly_cost": 760,
        "source": "oauth_discovery"
    },
    {
        "name": "GitHub",
        "owner": "Engineering",
        "license_count": 45,
        "monthly_cost": 900,
        "source": "sso_logs"
    },
    {
        "name": "Miro",
        "owner": "Product",
        "license_count": 22,
        "monthly_cost": 220,
        "source": "expense_report"
    },
    {
        "name": "Unknown AI Notes Tool",
        "owner": "Unknown",
        "license_count": 8,
        "monthly_cost": 160,
        "source": "expense_report"
    }
]


def discover_saas_apps():
    approved = []
    shadow_it = []

    for app in DISCOVERED_APPS:
        app_report = {
            "name": app["name"],
            "owner": app["owner"],
            "license_count": app["license_count"],
            "monthly_cost": app["monthly_cost"],
            "source": app["source"],
            "approved": app["name"] in APPROVED_APPS
        }

        if app_report["approved"]:
            approved.append(app_report)
        else:
            shadow_it.append(app_report)

    result = {
        "workflow": "saas_discovery",
        "total_apps": len(DISCOVERED_APPS),
        "approved_count": len(approved),
        "shadow_it_count": len(shadow_it),
        "approved_apps": approved,
        "shadow_it_apps": shadow_it,
        "status": "completed"
    }

    write_audit("saas_discovery", "completed", result)

    return result


def license_governance():
    discovery = discover_saas_apps()

    total_monthly_cost = 0
    total_licenses = 0

    for app in DISCOVERED_APPS:
        total_monthly_cost += app["monthly_cost"]
        total_licenses += app["license_count"]

    result = {
        "workflow": "license_governance",
        "total_licenses": total_licenses,
        "total_monthly_cost": total_monthly_cost,
        "shadow_it_count": discovery["shadow_it_count"],
        "status": "completed"
    }

    write_audit("license_governance", "completed", result)

    return result