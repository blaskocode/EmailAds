"""
Application configuration using Pydantic BaseSettings
"""
from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenAI
    OPENAI_API_KEY: str
    
    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/campaigns.db"
    
    # Application
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    
    # API Configuration
    API_RATE_LIMIT: int = 100
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB in bytes
    
    # Security - read as string from env, converted to list
    # Note: Field name must match env var name for Pydantic Settings
    ALLOWED_ORIGINS: Optional[str] = "http://localhost:3000,http://localhost:5173"
    
    @model_validator(mode='after')
    def parse_allowed_origins(self):
        """Convert comma-separated ALLOWED_ORIGINS string to list"""
        if isinstance(self.ALLOWED_ORIGINS, str):
            # Convert string to list and store back
            origins_list = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(',') if origin.strip()]
            # Use object.__setattr__ to set the attribute (bypassing Pydantic's validation)
            object.__setattr__(self, 'ALLOWED_ORIGINS', origins_list)
        return self
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

