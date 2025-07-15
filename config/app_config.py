"""
Application Configuration Module
Handles environment variables and application settings
"""

import os
from typing import List, Optional
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Main application configuration class"""
    
    # API Configuration
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Model Configuration
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "deepseek/deepseek-chat")
    FALLBACK_MODEL: str = os.getenv("FALLBACK_MODEL", "anthropic/claude-3-haiku-20240307")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Application Settings
    APP_NAME: str = os.getenv("APP_NAME", "Agentic AI Revenue Assistant")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Data Processing
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    SUPPORTED_FILE_TYPES: List[str] = os.getenv("SUPPORTED_FILE_TYPES", "csv,xlsx,xls").split(",")
    MAX_RECORDS: int = int(os.getenv("MAX_RECORDS", "10000"))
    
    # Privacy and Security
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    ENABLE_AUDIT_LOGGING: bool = os.getenv("ENABLE_AUDIT_LOGGING", "True").lower() == "true"
    
    # Three HK Branding
    PRIMARY_COLOR: str = os.getenv("PRIMARY_COLOR", "#00FF00")
    SECONDARY_COLOR: str = os.getenv("SECONDARY_COLOR", "#000000")
    ACCENT_COLOR: str = os.getenv("ACCENT_COLOR", "#FFFFFF")
    
    # Performance
    CACHE_TIMEOUT_SECONDS: int = int(os.getenv("CACHE_TIMEOUT_SECONDS", "300"))
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate configuration and return list of missing required settings"""
        missing = []
        
        if not cls.OPENROUTER_API_KEY:
            missing.append("OPENROUTER_API_KEY")
        
        if not cls.ENCRYPTION_KEY:
            missing.append("ENCRYPTION_KEY")
            
        return missing
    
    @classmethod
    def setup_directories(cls) -> None:
        """Create necessary directories if they don't exist"""
        directories = [
            cls.DATA_DIR,
            cls.RAW_DATA_DIR,
            cls.PROCESSED_DATA_DIR,
            cls.LOGS_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

# Global config instance
config = Config() 