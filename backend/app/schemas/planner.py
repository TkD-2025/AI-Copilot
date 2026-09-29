from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class IntentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    parsed_intent: dict[str, Any]
    confidence_score: float


class PlanCreate(BaseModel):
    intent_id: UUID
    status: str
    graph_snapshot: dict[str, Any] | None = None
    planner_name: str
    planner_version: str
    planner_latency_ms: int


class PlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    intent_id: UUID
    status: str
    graph_snapshot: dict[str, Any] | None = None
    planner_name: str
    planner_version: str
    planner_latency_ms: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
