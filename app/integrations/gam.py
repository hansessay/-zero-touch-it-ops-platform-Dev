import subprocess
from app.audit import write_audit


def _run_gam(command: list[str]):
    full_command = ["gam"] + command

    try:
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            timeout=120
        )

        response = {
            "command": " ".join(full_command),
            "status_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except FileNotFoundError:
        response = {
            "command": " ".join(full_command),
            "status_code": 127,
            "stdout": "",
            "stderr": "GAM is not installed or not available in PATH"
        }

    write_audit("gam_command", "completed", response)
    return response


def gam_info_user(email: str):
    return _run_gam(["info", "user", email])


def gam_print_users():
    return _run_gam(["print", "users"])


def gam_print_groups():
    return _run_gam(["print", "groups"])


def gam_group_members(group_email: str):
    return _run_gam(["print", "group-members", "group", group_email])


def gam_suspended_users():
    return _run_gam(["print", "users", "query", "isSuspended=true"])


def gam_drive_permissions(email: str):
    return _run_gam(["user", email, "print", "filelist", "fields", "id,name,permissions"])


def gam_email_forwards(email: str):
    return _run_gam(["user", email, "show", "forwardingaddresses"])