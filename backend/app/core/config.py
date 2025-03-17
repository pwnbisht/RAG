from typing import ClassVar, Set
from functools import lru_cache
from dotenv import load_dotenv

from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    algorithm: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    
    # security headers
    cookie_samesite: str
    
    # ratelimitting
    cors_origins: list[str]
    rate_limit_requests: int
    rate_limit_period: int
    
    # database
    database_url: str
    
    # other
    ALLOWED_FILE_EXTENSIONS: ClassVar[Set[str]] = {
        'pdf', 'csv', 'xls', 'xlsx',
        'docx', 'doc', 'txt', 'json'
    }
    MAX_FILE_SIZE: ClassVar[int] = 50 * 1024 * 1024
    
    # models
    ollama_url: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

class CsrfSettings(BaseSettings):
    CSRF_SECRET_KEY: str
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """Returns a cached instance of Settings to optimize performance."""
    return Settings()

@lru_cache
def get_csrf_settings() -> CsrfSettings:
    """Returns a cached instance of CsrfSettings."""
    return CsrfSettings()