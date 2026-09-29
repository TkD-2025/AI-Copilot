from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

PlanState = Literal["pending", "waiting_approval", "ready", "completed", "failed", "skipped"]


class PlanNodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    plan_id: UUID
    action_type: str
    action_payload: dict[str, Any] | None = None
    risk_level: str
    state: PlanState
    created_at: str | None = None
