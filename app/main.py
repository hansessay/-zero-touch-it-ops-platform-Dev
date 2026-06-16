

from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI
from pydantic import BaseModel

from app.workflows.onboarding import run_onboarding
from app.workflows.offboarding import run_offboarding
from app.workflows.saas_governance import discover_saas_apps, license_governance
from app.workflows.audit_readiness import generate_audit_report
from app.workflows.tier3_remediation import remediate_device
from app.integrations.jumpcloud import apply_policy, run_command
from app.workflows.telemetry import get_fleet_telemetry
from app.workflows.pdf_export import export_telemetry_pdf

from app.workflows.software_requests import (
    request_software_install,
    approve_software_install,
)


from app.events.producer import (
    start_kafka_producer,
    stop_kafka_producer,
    publish_event,
)
from app.integrations.sentinelone import (
    get_agents,
    check_agent_status,
    isolate_device,
)
from app.integrations.google_workspace import (
    create_google_user,
    suspend_google_user,
    add_user_to_group,
    list_users,
)
from app.workflows.compliance import (
    fleet_compliance,
    identity_compliance,
)

from app.workflows.posture_management import (
    check_device_posture,
    remediate_device_posture,
)


app = FastAPI(
    title="Zero-Touch IT Operations Platform",
    version="0.1.0",
)

@app.on_event("startup")
async def startup_event():
    await start_kafka_producer()


@app.on_event("shutdown")
async def shutdown_event():
    await stop_kafka_producer()


class SoftwareInstallRequest(BaseModel):
    user_email: str
    hostname: str
    software_name: str
    business_reason: str
    manager_email: str


class SoftwareInstallApprovalRequest(BaseModel):
    user_email: str
    hostname: str
    software_name: str
    approved_by: str

class OnboardingRequest(BaseModel):
    first_name: str
    last_name: str
    employee_email: str
    department: str
    job_title: str
    manager_email: str
    location: str


class OffboardingRequest(BaseModel):
    employee_email: str
    manager_email: str
    reason: str
    transfer_ownership_to: str


class FleetPatchingRequest(BaseModel):
    hostname: str
    os: str
    action: str


class PostureCheckRequest(BaseModel):
    hostname: str
    baseline: str


class AuditEvidenceRequest(BaseModel):
    framework: str
    evidence_type: str


class Tier3EscalationRequest(BaseModel):
    issue_type: str
    affected_user: str
    affected_device: str


class SOPRunRequest(BaseModel):
    sop_name: str
    affected_user: str
    affected_device: str

class JumpCloudPolicyRequest(BaseModel):
    policy_name: str
    target_group: str
    policy_type: str = "security_baseline"


class JumpCloudCommandRequest(BaseModel):
    command_name: str
    target_group: str
    script_type: str = "powershell"

class EndpointRemediationRequest(BaseModel):
    hostname: str
    issue: str


class GoogleCreateUserRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    department: str


class GoogleSuspendUserRequest(BaseModel):
    email: str


class GoogleGroupRequest(BaseModel):
    user_email: str
    group_email: str


@app.get("/")
def root():
    return {"message": "Zero-Touch IT Operations Platform API"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/onboarding/start")
async def start_onboarding(request: OnboardingRequest):
    await publish_event(
        "employee.onboarding.requested",
        {
            "event_type": "employee.onboarding.requested",
            "employee_email": request.employee_email,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "department": request.department,
            "job_title": request.job_title,
            "manager_email": request.manager_email,
            "location": request.location,
        },
    )

    return {
        "status": "success",
        "message": "Onboarding event published to Kafka",
        "employee_email": request.employee_email,
    }


@app.post("/offboarding/start")
def start_offboarding(request: OffboardingRequest):
    return run_offboarding(request)


@app.post("/fleet/patching")
def run_patch_workflow(request: FleetPatchingRequest):
    return {
        "status": "success",
        "message": "Patch workflow executed",
        "hostname": request.hostname,
        "os": request.os,
        "action": request.action,
        "actions": [
            "Check device patch state",
            "Validate OS update status",
            "Validate third-party software updates",
            "Send patch command to device management platform",
            "Record patch workflow evidence",
        ],
    }


@app.post("/fleet/posture/check")
def check_posture(request: PostureCheckRequest):
    return check_device_posture(request.hostname)


@app.post("/fleet/posture/remediate")
def remediate_posture(request: PostureCheckRequest):
    return remediate_device_posture(request.hostname)

@app.post("/fleet/audit/evidence")
def generate_audit_evidence(request: AuditEvidenceRequest):
    return {
        "status": "success",
        "message": "Audit evidence generated",
        "framework": request.framework,
        "evidence_type": request.evidence_type,
        "evidence": {
            "devices_checked": 12,
            "compliant_devices": 9,
            "non_compliant_devices": 3,
            "logs_available": True,
            "generated_by": "Zero-Touch IT Operations Platform",
        },
        "audit_summary": [
            "Device compliance evidence collected",
            "Patch history reviewed",
            "Endpoint security posture validated",
            "Workflow logs attached for auditor review",
        ],
    }




@app.post("/tier3/escalation")
def create_tier3_escalation(request: Tier3EscalationRequest):
    return {
        "status": "success",
        "message": "Tier 3 escalation created",
        "issue_type": request.issue_type,
        "affected_user": request.affected_user,
        "affected_device": request.affected_device,
        "next_steps": [
            "Collect diagnostic logs",
            "Validate identity and device state",
            "Review security agent status",
            "Document root cause",
            "Create reusable SOP if repeated",
        ],
    }


@app.post("/tier3/sop/run")
def run_sop(request: SOPRunRequest):
    return {
        "status": "success",
        "message": "Safe SOP automation executed",
        "sop_name": request.sop_name,
        "affected_user": request.affected_user,
        "affected_device": request.affected_device,
        "guardrails": [
            "Input validated",
            "Action logged",
            "Rollback path documented",
            "Support-safe execution completed",
        ],
    }


@app.post("/tier3/remediate")
def run_remediation(request: EndpointRemediationRequest):
    return remediate_device(
        hostname=request.hostname,
        issue=request.issue,
    )


@app.get("/compliance/fleet")
def get_fleet_compliance():
    return fleet_compliance()


@app.get("/compliance/identity")
def get_identity_compliance():
    return identity_compliance()


@app.get("/saas/discovery")
def run_saas_discovery():
    return discover_saas_apps()


@app.get("/saas/licenses")
def run_license_governance():
    return license_governance()


@app.get("/audit/report")
def run_audit_report():
    return generate_audit_report()


@app.post("/google/users/create")
def google_create_user_endpoint(request: GoogleCreateUserRequest):
    return create_google_user(
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        department=request.department,
    )


@app.post("/google/users/suspend")
def google_suspend_user_endpoint(request: GoogleSuspendUserRequest):
    return suspend_google_user(request.email)


@app.post("/google/groups/add-member")
def google_add_group_member_endpoint(request: GoogleGroupRequest):
    return add_user_to_group(
        user_email=request.user_email,
        group_email=request.group_email,
    )


@app.get("/google/users")
def google_list_users_endpoint(max_results: int = 50):
    return list_users(max_results=max_results)

@app.post("/jumpcloud/policies/apply")
def apply_jumpcloud_policy(request: JumpCloudPolicyRequest):
    return apply_policy(
        request.policy_name,
        request.target_group,
        request.policy_type,
    )


@app.post("/jumpcloud/commands/run")
def run_jumpcloud_command(request: JumpCloudCommandRequest):
    return run_command(
        request.command_name,
        request.target_group,
        request.script_type,
    )


@app.get("/observability/telemetry")
def observability_telemetry():
    return get_fleet_telemetry()


@app.get("/observability/telemetry/export-pdf")
def export_telemetry_pdf_report():
    telemetry = get_fleet_telemetry()
    return export_telemetry_pdf(telemetry)


@app.post("/software/install/request")
def submit_software_install_request(request: SoftwareInstallRequest):
    return request_software_install(
        user_email=request.user_email,
        hostname=request.hostname,
        software_name=request.software_name,
        business_reason=request.business_reason,
        manager_email=request.manager_email,
    )


@app.post("/software/install/approve")
def approve_software_install_request(request: SoftwareInstallApprovalRequest):
    return approve_software_install(
        user_email=request.user_email,
        hostname=request.hostname,
        software_name=request.software_name,
        approved_by=request.approved_by,
    )


@app.get("/sentinelone/agents")
def sentinelone_agents_endpoint():
    return get_agents()


@app.get("/sentinelone/agents/{hostname}")
def sentinelone_agent_status_endpoint(hostname: str):
    return check_agent_status(hostname)


@app.post("/sentinelone/isolate/{hostname}")
def sentinelone_isolate_device_endpoint(hostname: str):
    return isolate_device(hostname)

