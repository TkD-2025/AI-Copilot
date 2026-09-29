from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

ExecutionStatus = Literal["running", "succeeded", "failed", "cancelled", "timed_out"]


class EnvironmentCreate(BaseModel):
    name: str
    type: str
    connection_config: dict[str, Any] | None = None
    is_sandboxed: bool
    status: str


class EnvironmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    type: str
    connection_config: dict[str, Any] | None = None
    is_sandboxed: bool
    status: str
    created_at: str | None = None


class ExecutionCreate(BaseModel):
    plan_node_id: UUID
    environment_id: UUID
    attempt_number: int = 1
    started_at: str
    finished_at: str | None = None
    status: ExecutionStatus
    risk_score: float | None = None
    output: dict[str, Any] | None = None
    error_message: str | None = None


class ExecutionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    plan_node_id: UUID
    environment_id: UUID
    attempt_number: int
    started_at: str
    finished_at: str | None = None
    status: ExecutionStatus
    risk_score: float | None = None
    output: dict[str, Any] | None = None
    error_message: str | None = None
    created_at: str | None = None


class ExecutionObservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    execution_id: UUID
    observation_type: str
    data: dict[str, Any]
    validated: bool
    created_at: str | None = None
