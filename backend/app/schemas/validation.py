from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

ApprovalDecision = Literal["approved", "rejected", "modified"]


class SafetyRuleCreate(BaseModel):
    rule_name: str
    pattern: dict[str, Any]
    rule_type: str
    risk_weight: float
    active: bool


class SafetyRuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    rule_name: str
    pattern: dict[str, Any]
    rule_type: str
    risk_weight: float
    active: bool


class NodeApprovalCreate(BaseModel):
    plan_node_id: UUID
    requested_by: str
    decided_by: UUID | None = None
    decision: ApprovalDecision
    comment: str | None = None
    decided_at: str | None = None


class NodeApprovalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    plan_node_id: UUID
    requested_by: str
    decided_by: UUID | None = None
    decision: ApprovalDecision
    comment: str | None = None
    decided_at: str | None = None


class PermissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None = None
    action_type: str
    allowed: bool
    scope: dict[str, Any] | None = None
