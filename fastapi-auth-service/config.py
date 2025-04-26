from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn


class Settings(BaseSettings):
    # Seguridad
    JWT_SECRET_KEY: str
    JWT_LIFETIME_SECONDS: int

    # Base de datos
    DATABASE_URL: PostgresDsn  # validará que la URL esté bien formada
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # Configuración de carga desde `.env`
    model_config = SettingsConfigDict(
        env_file=".env", extra="forbid"
    )  # no permite variables no definidas


def get_settings() -> Settings:
    return Settings()
