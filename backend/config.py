from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    
    google_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    llm_provider: str = "gemini"
    llm_model: str = "gemini-2.0-flash"
    
    database_url: str = "sqlite:///./agentguard.db"
    
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    admin_api_key: str = "dev-secret"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

settings = Settings()

def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
