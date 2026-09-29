from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


from enum import Enum

class TaskStatus(str, Enum):
    CREATED = "CREATED"
    PLANNED = "PLANNED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class TaskCreate(BaseModel):
    session_id: UUID
    prompt: str


class TaskResponse(BaseModel):
    task_id: UUID
    plan_id: UUID
    status: TaskStatus


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: UUID
    session_id: UUID
    prompt: str
    status: TaskStatus
    created_at: datetime | None = None
