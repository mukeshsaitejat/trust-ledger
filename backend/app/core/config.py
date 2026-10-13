"""
Configuration settings for InvoiceShield.
Loads from environment variables with sensible defaults.
"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application configuration."""
    
    # Application
    app_name: str = "InvoiceShield"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Storage
    upload_dir: str = "storage/documents"
    max_upload_size_mb: int = 10
    allowed_extensions: set = {".pdf"}
    
    # Database
    database_url: str = "sqlite:///./invoiceshield.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def max_upload_size_bytes(self) -> int:
        """Convert MB to bytes."""
        return self.max_upload_size_mb * 1024 * 1024
    
    @property
    def upload_path(self) -> Path:
        """Get upload directory as Path object."""
        return Path(self.upload_dir)


# Global settings instance
settings = Settings()
