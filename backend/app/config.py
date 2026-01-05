"""
Configuration management for Neuro-Privacy Guard backend.
Loads settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Neuro-Privacy-Guard"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    FRONTEND_URL: str = "http://localhost:5500,http://127.0.0.1:5500"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [url.strip() for url in self.FRONTEND_URL.split(",")]
    
    # Privacy Engine
    DEFAULT_PRIVACY_LEVEL: float = 0.5
    DEFAULT_EPSILON: float = 1.0
    DEFAULT_DELTA: float = 0.00001
    
    # Security
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    ENABLE_ENCRYPTED_LOGS: bool = False
    
    # ML Models
    MODEL_PATH: str = "./ml_models"
    INTENT_MODEL_FILE: str = "intent_classifier.pkl"
    
    @property
    def intent_model_path(self) -> str:
        """Full path to intent classification model."""
        return os.path.join(self.MODEL_PATH, self.INTENT_MODEL_FILE)
    
    # EEG Signal Settings
    SAMPLING_RATE: int = 256  # Hz
    NUM_CHANNELS: int = 8
    SIGNAL_DURATION: float = 2.0  # seconds
    
    # Database (optional)
    DATABASE_URL: str = "sqlite:///./npg.db"
    
    # Azure (optional)
    COSMOS_ENDPOINT: str = ""
    COSMOS_KEY: str = ""
    COSMOS_DATABASE: str = "npg-database"
    AZURE_KEY_VAULT_URL: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
