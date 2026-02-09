from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,  # extra=
    )

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACESS_TOKEN_EXPIRE_MINUTES: int


class ToDoState(str, Enum):
    draft = "draft"
    todo = "todo"
    doing = "doing"
    done = "done"
    trash = "trash"


settings = Settings()
