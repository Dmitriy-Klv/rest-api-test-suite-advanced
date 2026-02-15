import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")


class Settings(BaseSettings):
    BASE_API_URL: str = Field(default="https://dummyjson.com")
    REQUEST_TIMEOUT: int = Field(default=10)
    LOG_LEVEL: str = Field(default="INFO")

    TEST_USERNAME: str
    TEST_PASSWORD: SecretStr

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()