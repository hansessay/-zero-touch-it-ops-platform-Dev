from app.audit import write_audit


def remediate_endpoint(hostname: str, os: str, issue: str):
    if os.lower() == "windows":
        script = "PowerShell remediation selected"
    elif os.lower() == "macos":
        script = "Bash remediation selected"
    else:
        script = "Unsupported OS"

    result = {
        "hostname": hostname,
        "os": os,
        "issue": issue,
        "script": script,
        "status": "simulated_success"
    }

    write_audit("endpoint_remediation", "success", result)
    return result