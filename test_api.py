import requests

API_URL = "http://127.0.0.1:8001"


def test_get(path):
    response = requests.get(f"{API_URL}{path}")
    print(f"\nGET {path}")
    print(response.status_code)
    print(response.json())


def test_post(path, payload):
    response = requests.post(f"{API_URL}{path}", json=payload)
    print(f"\nPOST {path}")
    print(response.status_code)
    print(response.json())


test_get("/health")

test_post("/offboarding/start", {
    "email": "john.doe@company.com",
    "manager_email": "manager@company.com",
    "reason": "termination",
    "transfer_owner": "manager@company.com"
})

test_post("/jumpcloud/commands/run", {
    "command_name": "Check BitLocker Status",
    "target_group": "Windows-Laptops",
    "script_type": "powershell"
})

test_post("/jumpcloud/policies/apply", {
    "policy_name": "Disk Encryption Policy",
    "target_group": "All-Windows-Devices",
    "policy_type": "security"
})

test_post("/google/groups/add-user", {
    "user_email": "john.doe@company.com",
    "group_email": "engineering@company.com"
})

test_post("/endpoint/remediate", {
    "hostname": "laptop-001",
    "os": "windows",
    "issue": "bitlocker_disabled"
})

test_get("/audit")
test_get("/workflows/history")