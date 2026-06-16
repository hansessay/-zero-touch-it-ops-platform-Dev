from app.audit import write_audit
from app.integrations.jumpcloud import run_command


SOFTWARE_CATALOG = {
    "chrome": {
        "display_name": "Google Chrome",
        "install_command": "Install Google Chrome",
        "requires_manager_approval": True,
    },
    "vscode": {
        "display_name": "Visual Studio Code",
        "install_command": "Install Visual Studio Code",
        "requires_manager_approval": True,
    },
}


def request_software_install(
    user_email: str,
    hostname: str,
    software_name: str,
    business_reason: str,
    manager_email: str,
):
    result = {
        "workflow": "software_install_request",
        "user_email": user_email,
        "hostname": hostname,
        "software_name": software_name,
        "business_reason": business_reason,
        "manager_email": manager_email,
        "approval_status": "pending_manager_approval",
        "status": "submitted",
    }

    write_audit("software_install_request", "submitted", result)
    return result


def approve_software_install(
    user_email: str,
    hostname: str,
    software_name: str,
    approved_by: str,
):
    software = SOFTWARE_CATALOG.get(software_name.lower())

    if not software:
        result = {
            "workflow": "software_install_approval",
            "user_email": user_email,
            "hostname": hostname,
            "software_name": software_name,
            "approved_by": approved_by,
            "status": "rejected",
            "reason": "software_not_in_approved_catalog",
        }

        write_audit("software_install_approval", "rejected", result)
        return result

    install_result = run_command(
        command_name=software["install_command"],
        target_group="Engineering",
        script_type="powershell",
    )

    result = {
        "workflow": "software_install_approval",
        "user_email": user_email,
        "hostname": hostname,
        "software_name": software["display_name"],
        "approved_by": approved_by,
        "approval_status": "approved",
        "install_action": install_result,
        "status": "completed",
    }

    write_audit("software_install_approval", "completed", result)
    return result