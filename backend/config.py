from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Ollama Configuration
    ollama_host: str = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")
    ollama_model_primary: str = "mistral"
    ollama_model_secondary: str = "llama3"
    ollama_model_tertiary: str = "qwen2"
    
    # MongoDB Configuration
    mongo_url: str = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    db_name: str = os.environ.get("DB_NAME", "test_database")
    
    # API Security
    api_secret_key: str = os.environ.get("API_SECRET_KEY", "development-secret-key")
    cors_origins: str = os.environ.get("CORS_ORIGINS", "*")
    
    # Application Settings
    debug: bool = os.environ.get("DEBUG", "false").lower() == "true"
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> list:
        """Convert comma-separated origins to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

def get_settings() -> Settings:
    """Get settings instance with caching"""
    return Settings()