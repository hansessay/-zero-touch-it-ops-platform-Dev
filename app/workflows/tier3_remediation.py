from app.audit import write_audit


def remediate_device(hostname: str, issue: str):
    actions = []

    normalized_issue = issue.lower()

    if normalized_issue == "sentinelone":
        actions.append("Validate SentinelOne agent status")
        actions.append("Collect endpoint protection logs")
        actions.append("Reinstall SentinelOne agent if missing")
        actions.append("Escalate to security if agent remains unhealthy")

    elif normalized_issue == "bitlocker":
        actions.append("Validate BitLocker encryption status")
        actions.append("Apply disk encryption policy")
        actions.append("Collect encryption compliance evidence")

    elif normalized_issue == "patching":
        actions.append("Check missing OS and third-party patches")
        actions.append("Trigger patch deployment")
        actions.append("Validate post-patch state")

    elif normalized_issue == "identity":
        actions.append("Validate Google Workspace user state")
        actions.append("Validate JumpCloud user state")
        actions.append("Check group membership and RBAC assignment")

    else:
        actions.append("Collect diagnostics")
        actions.append("Validate endpoint and identity state")
        actions.append("Escalate to engineering for manual review")

    result = {
        "workflow": "tier3_remediation",
        "hostname": hostname,
        "issue": issue,
        "actions": actions,
        "status": "completed",
    }

    write_audit(
        "tier3_remediation",
        "completed",
        result,
    )

    return result