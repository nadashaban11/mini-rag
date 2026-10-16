from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from ..llm.enums import LLMEnums


class Settings(BaseSettings):

    FILE_ALLOWED_TYPES: list[str]
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5433
    POSTGRES_DB: str

    GENERATION_BACKEND: LLMEnums = LLMEnums.OPENAI
    EMBEDDING_BACKEND: LLMEnums = LLMEnums.OPENAI

    OPENAI_API_KEY: SecretStr | None = None
    OPENAI_BASE_URL: str | None = None

    GENERATION_MODEL_ID: str
    EMBEDDING_MODEL_ID: str
    EMBEDDING_SIZE: int
    GENERATION_DEFAULT_MAX_TOKENS: int = 1000
    GENERATION_DEFAULT_TEMPERATURE: float = 0.1

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()