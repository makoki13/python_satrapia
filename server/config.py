# server/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración del servidor FastAPI."""

    # Servidor
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Juego
    TURN_DURATION_SECONDS: int = 60  # Duración de cada turno (1 minuto)
    MAX_PLAYERS_PER_GAME: int = 8

    # Seguridad (para más adelante)
    SECRET_KEY: str = "satrapia-secret-key-cambiar-en-produccion"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

# Instancia global de la configuración
settings = Settings()
