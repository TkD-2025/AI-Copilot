from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/ai_copilot"
    )
    DB_ECHO: bool = False


settings = Settings()
