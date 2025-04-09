# services/task-service/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str = "postgresql+asyncpg://task_user:task_password@localhost:5432/task_db"
    # If running FastAPI inside Docker later, hostname will be 'postgres_db'
    # DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://task_user:task_password@postgres_db:5432/task_db")

    # Keycloak Configuration (Move existing ones here)
    KEYCLOAK_URL: str = "http://localhost:8080"
    # If running FastAPI inside Docker later, hostname might be 'keycloak' or use host.docker.internal
    # KEYCLOAK_URL: str = os.getenv("KEYCLOAK_URL", "http://host.docker.internal:8080")
    REALM_NAME: str = "task-app-realm"
    # We fetch the public key dynamically, so no need to store it here

    # Allow configuring via environment variables (optional but good practice)
    class Config:
        env_file = '.env' # Load from a .env file if it exists
        extra = 'ignore' # Ignore extra fields from .env

settings = Settings()

# --- Dynamic Keycloak Public Key Fetching (Keep this logic in main.py or move to a dedicated auth module) ---
# It's generally better to keep the public key fetching logic separate from static config
KEYCLOAK_PUBLIC_KEY = None