import streamlit as st
import requests

API_URL = "http://127.0.0.1:8001"

st.set_page_config(
    page_title="Zero-Touch IT Operations Platform",
    page_icon="⚙️",
    layout="wide"
)

st.title("Zero-Touch IT Operations Platform")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "HR Onboarding Portal",
        "HR Offboarding Portal",
        "Fleet Reliability & Compliance",
        "Observability & Data Integrity",
        "Tier 3 Escalation & SOPs",
    ]
)


with tab1:
    st.header("Employee Onboarding")

    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    employee_email = st.text_input("Employee Email")
    department = st.text_input("Department")
    job_title = st.text_input("Job Title")
    manager_email = st.text_input("Manager Email")
    location = st.text_input("Location")

    if st.button("Create Employee"):
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "employee_email": employee_email,
            "department": department,
            "job_title": job_title,
            "manager_email": manager_email,
            "location": location,
        }

        response = requests.post(f"{API_URL}/onboarding/start", json=payload)

        if response.status_code == 200:
            st.success("Onboarding workflow started")
            st.json(response.json())
        else:
            st.error("Onboarding failed")
            st.write(response.text)


with tab2:
    st.header("Employee Offboarding")

    employee_email = st.text_input("Employee Email", key="off_employee_email")
    manager_email = st.text_input("Manager Email", key="off_manager_email")
    reason = st.selectbox("Reason", ["termination", "resignation", "internal_transfer"])
    transfer_ownership_to = st.text_input("Transfer ownership to")

    if st.button("Offboard Employee"):
        payload = {
            "employee_email": employee_email,
            "manager_email": manager_email,
            "reason": reason,
            "transfer_ownership_to": transfer_ownership_to,
        }

        response = requests.post(f"{API_URL}/offboarding/start", json=payload)

        if response.status_code == 200:
            st.success("Offboarding workflow started")
            st.json(response.json())
        else:
            st.error("Offboarding failed")
            st.write(response.text)


with tab3:
    st.header("Fleet Reliability & Compliance")

    st.subheader("Automated Patching")

    hostname = st.text_input("Device Hostname", value="laptop-001")
    os_type = st.selectbox("Operating System", ["Windows 11", "Windows 10", "macOS", "Linux"])

    patch_action = st.selectbox(
        "Patch Action",
        [
            "check_patch_status",
            "schedule_os_patch",
            "schedule_third_party_patch",
            "force_patch_now",
        ],
    )

    if st.button("Run Patch Workflow"):
        payload = {
            "hostname": hostname,
            "os": os_type,
            "action": patch_action,
        }

        response = requests.post(f"{API_URL}/fleet/patching", json=payload)

        if response.status_code == 200:
            st.success("Patch workflow executed")
            st.json(response.json())
        else:
            st.error("Patch workflow failed")
            st.write(response.text)

    st.divider()

    st.subheader("Posture Management")

    posture_hostname = st.text_input("Device Hostname", value="laptop-001", key="posture_hostname")

    baseline = st.selectbox(
        "Desired Security Baseline",
        [
            "standard_employee",
            "engineering",
            "privileged_admin",
            "remote_worker",
        ],
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Check Desired State"):
            payload = {
                "hostname": posture_hostname,
                "baseline": baseline,
            }

            response = requests.post(f"{API_URL}/fleet/posture/check", json=payload)

            if response.status_code == 200:
                st.success("Posture check completed")
                st.json(response.json())
            else:
                st.error("Posture check failed")
                st.write(response.text)

    with col2:
        if st.button("Remediate Drift"):
            payload = {
                "hostname": posture_hostname,
                "baseline": baseline,
            }

            response = requests.post(f"{API_URL}/fleet/posture/remediate", json=payload)

            if response.status_code == 200:
                st.success("Remediation workflow started")
                st.json(response.json())
            else:
                st.error("Remediation failed")
                st.write(response.text)

    st.divider()

    st.subheader("Audit Readiness")

    audit_framework = st.selectbox(
        "Audit Framework",
        ["SOC2", "ISO27001", "Internal Security Review"],
    )

    evidence_type = st.selectbox(
        "Evidence Type",
        [
            "device_compliance",
            "patch_history",
            "access_review",
            "endpoint_security",
            "workflow_logs",
        ],
    )

    if st.button("Generate Audit Evidence"):
        payload = {
            "framework": audit_framework,
            "evidence_type": evidence_type,
        }

        response = requests.post(f"{API_URL}/fleet/audit/evidence", json=payload)

        if response.status_code == 200:
            st.success("Audit evidence generated")
            st.json(response.json())
        else:
            st.error("Audit evidence generation failed")
            st.write(response.text)


with tab4:
    st.header("Observability & Data Integrity")

    st.subheader("SaaS Discovery")

    if st.button("Run SaaS Discovery"):
        response = requests.get(f"{API_URL}/saas/discovery")

        if response.status_code == 200:
            st.success("SaaS discovery completed")
            st.json(response.json())
        else:
            st.error(response.text)

    st.divider()

    st.subheader("Telemetry Dashboard")

    if st.button("Get Fleet Telemetry"):
        response = requests.get(f"{API_URL}/observability/telemetry")

        if response.status_code == 200:
            st.success("Telemetry loaded")
            st.json(response.json())
        else:
            st.error(response.text)


with tab5:
    st.header("Tier 3 Escalation & Standard Operating Procedures")

    st.subheader("Complex Endpoint / Identity Issue")

    issue_type = st.selectbox(
        "Issue Type",
        [
            "endpoint_not_compliant",
            "identity_access_issue",
            "security_agent_failure",
            "device_enrollment_failure",
            "unknown_complex_issue",
        ],
    )

    affected_user = st.text_input("Affected User Email")
    affected_device = st.text_input("Affected Device Hostname")

    if st.button("Create Tier 3 Escalation"):
        payload = {
            "issue_type": issue_type,
            "affected_user": affected_user,
            "affected_device": affected_device,
        }

        response = requests.post(
            f"{API_URL}/tier3/escalation",
            json=payload,
        )

        if response.status_code == 200:
            st.success("Tier 3 escalation created")
            st.json(response.json())
        else:
            st.error(response.text)

    st.divider()

    st.subheader("Paved Road Automation")

    sop_name = st.selectbox(
        "SOP / Automation",
        [
            "reset_user_mfa",
            "re_enroll_device",
            "restart_security_agent",
            "collect_device_diagnostics",
            "validate_access_groups",
        ],
    )

    if st.button("Run Safe SOP Automation"):
        payload = {
            "sop_name": sop_name,
            "affected_user": affected_user,
            "affected_device": affected_device,
        }

        response = requests.post(
            f"{API_URL}/tier3/sop/run",
            json=payload,
        )

        if response.status_code == 200:
            st.success("SOP automation executed")
            st.json(response.json())
        else:
            st.error(response.text)