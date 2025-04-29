from pydantic_settings import BaseSettings
from pydantic import PostgresDsn


class Settings(BaseSettings):
    # Seguridad
    JWT_SECRET_KEY: str
    JWT_LIFETIME_SECONDS: int

    # Base de datos
    DATABASE_URL: PostgresDsn  
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # Configuración de carga desde `.env`
    class Config:
        env_file = ".env"
        extra = "forbid"
        validate_by_name = True


def get_settings() -> Settings:
    return Settings()
