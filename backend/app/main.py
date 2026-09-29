from fastapi import FastAPI
from app.api import task_router

app = FastAPI()

app.include_router(task_router.router)