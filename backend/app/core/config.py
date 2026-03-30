from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración central de la aplicación.
    Pydantic lee automáticamente estas variables del fichero .env
    y valida que tengan el tipo correcto.
    """

    # --- Base de datos ---
    DATABASE_URL: str

    # --- Redis ---
    REDIS_URL: str = "redis://redis:6379/0"

    # --- Seguridad JWT ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- GROQ ---
    GROQ_API_KEY: str = "PENDIENTE_FASE_4"

    # --- Entorno ---
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        # Busca el .env en la carpeta del backend
        env_file=".env",
        # Si hay variables extra en el .env que no están aquí, las ignora
        extra="ignore",
        # Permite que los valores se lean también de las variables
        # de entorno del sistema (lo que Docker inyecta via 'environment:')
        case_sensitive=True,
    )


# Instancia única que se importa en todo el proyecto
# En lugar de crear Settings() en cada fichero, importas este objeto
settings = Settings()