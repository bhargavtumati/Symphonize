import os
from enum import Enum

from pydantic import AnyHttpUrl, PostgresDsn, validator
from pydantic_settings import BaseSettings


class ModeEnum(str, Enum):
    development = "development"
    production = "production"
    testing = "testing"


class Settings(BaseSettings, extra="ignore"):
    PROJECT_NAME: str = "app"
    BACKEND_CORS_ORIGINS: list[str] | list[AnyHttpUrl] = ['*']
    MODE: ModeEnum = ModeEnum.development
    API_VERSION: str = "v1"
    API_V1_STR: str = f"/api/{API_VERSION}"
    WHEATER_URL: str = "https://wttr.in"
    DATABASE_URI: str = (os.getenv("DATABASE_URL").replace("%%","%"))
    CLASSIFIER_VERSION:str = "v0.001-07"
    VECTORIZER_VERSION:str = "v0.001-07"

    class Config:
        case_sensitive = True
        env_file = os.path.expanduser("../../.env")


settings = Settings()
