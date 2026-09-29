from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.task import TaskCreate, TaskOut, TaskResponse
from app.services import task_service

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    return task_service.create_task(task, db)


@router.get(
    "",
    response_model=List[TaskOut],
    status_code=status.HTTP_200_OK
)
def list_tasks(
    db: Session = Depends(get_db)
):
    return task_service.list_tasks(db)


@router.get(
    "/{task_id}",
    response_model=TaskOut,
    status_code=status.HTTP_200_OK
)
def get_task(
    task_id: UUID,
    db: Session = Depends(get_db)
):
    return task_service.get_task(task_id, db)