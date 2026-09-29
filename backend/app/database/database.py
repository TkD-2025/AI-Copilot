from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=settings.DB_ECHO, future=True)
Base = declarative_base()
