from pydantic import BaseModel
from typing import Optional


class UserRequest(BaseModel):
    email: str
    full_name: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    manager_email: Optional[str] = None


class OnboardingRequest(BaseModel):
    full_name: str
    email: str
    department: str
    role: str
    manager_email: str


class OffboardingRequest(BaseModel):
    email: str
    manager_email: str
    reason: str
    transfer_owner: Optional[str] = None


class JumpCloudCommandRequest(BaseModel):
    command_name: str
    target_group: str
    script_type: str


class JumpCloudPolicyRequest(BaseModel):
    policy_name: str
    target_group: str
    policy_type: str


class GoogleGroupRequest(BaseModel):
    user_email: str
    group_email: str


class EndpointRemediationRequest(BaseModel):
    hostname: str
    os: str
    issue: str