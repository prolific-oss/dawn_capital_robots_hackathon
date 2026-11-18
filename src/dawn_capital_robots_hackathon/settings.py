from functools import lru_cache

from pydantic import SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # read from ./.env; a real OPENAI_API_KEY environment variable takes precedence
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: SecretStr


@lru_cache
def get_settings():
    try:
        return Settings()
    except ValidationError as e:
        raise RuntimeError("OPENAI_API_KEY is not set: add it to .env or the environment") from e
