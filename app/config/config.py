from pydantic_settings import BaseSettings
from pydantic import ConfigDict, PostgresDsn, AnyHttpUrl
from typing import List


class Settings(BaseSettings):
    """
    Configuración principal de la aplicación, cargada desde variables de entorno.
    Usa pydantic para validación y tipado.
    """
    # Seguridad
    JWT_SECRET_KEY: str
    JWT_LIFETIME_SECONDS: int
    JWT_ALGORITHM: str
    COOKIE_NAME: str
    

    # CORS
    ALLOWED_ORIGINS: List[AnyHttpUrl]

    # Base de datos
    DATABASE_URL: PostgresDsn
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DB_ECHO: bool = False

    # Configuración de carga desde `.env`
    model_config = ConfigDict(
        env_file=".env",
        extra="forbid",
        validate_by_name=True,
    )
   

def get_settings() -> Settings:
    """
    Devuelve la configuración singleton de la aplicación.
    """
    # Singleton para evitar recarga múltiple
    if not hasattr(get_settings, "_settings"):
        get_settings._settings = Settings()
    return get_settings._settings
