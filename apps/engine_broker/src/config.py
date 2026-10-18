import os
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel as BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "OmniSwarm Dynamic Engine Broker"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Storage & State
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://omniswarm:omniswarm_secret@localhost:5432/omniswarm_db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Sidecar Engine URLs
    LANGGRAPH_SIDECAR_URL: str = os.getenv("LANGGRAPH_SIDECAR_URL", "http://sidecar-langgraph:8100")
    CREWAI_SIDECAR_URL: str = os.getenv("CREWAI_SIDECAR_URL", "http://sidecar-crewai:8200")
    AUTOGEN_SIDECAR_URL: str = os.getenv("AUTOGEN_SIDECAR_URL", "http://sidecar-autogen:8300")
    N8N_SIDECAR_URL: str = os.getenv("N8N_SIDECAR_URL", "http://n8n:5678")
    TEMPORAL_SIDECAR_URL: str = os.getenv("TEMPORAL_SIDECAR_URL", "http://temporal:7233")

    # Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "omniswarm-dev-secret-key-32chars-min-len!!")
    AUTH_ENABLED: bool = os.getenv("AUTH_ENABLED", "false").lower() == "true"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
