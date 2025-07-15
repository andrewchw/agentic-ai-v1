"""
Logging utility for the Agentic AI Revenue Assistant
Handles application logging with privacy-aware features
"""

import logging
import sys
from pathlib import Path
from config.app_config import config
from loguru import logger

def setup_logging():
    """Setup application logging with privacy protection"""
    
    # Create logs directory if it doesn't exist
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Remove default loguru handler
    logger.remove()
    
    # Add console handler with appropriate level
    logger.add(
        sys.stderr,
        level=config.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # Add file handler for application logs
    logger.add(
        config.LOGS_DIR / "app.log",
        level=config.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    # Add separate file handler for audit logs (privacy-sensitive)
    if config.ENABLE_AUDIT_LOGGING:
        logger.add(
            config.LOGS_DIR / "audit.log",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | AUDIT | {message}",
            rotation="10 MB",
            retention="90 days",  # Longer retention for audit logs
            compression="zip",
            filter=lambda record: "AUDIT" in record["message"]
        )
    
    logger.info(f"Logging initialized for {config.APP_NAME} v{config.APP_VERSION}")

def log_audit(message: str, user_id: str = "anonymous", action: str = ""):
    """Log audit trail for privacy-sensitive operations"""
    if config.ENABLE_AUDIT_LOGGING:
        logger.info(f"AUDIT | User: {user_id} | Action: {action} | {message}")

def sanitize_log_message(message: str) -> str:
    """Remove potentially sensitive information from log messages"""
    # Add patterns to remove sensitive data before logging
    sensitive_patterns = [
        "password", "token", "key", "secret",
        "email", "phone", "hkid", "name"
    ]
    
    sanitized = message
    for pattern in sensitive_patterns:
        if pattern.lower() in sanitized.lower():
            sanitized = sanitized.replace(pattern, "[REDACTED]")
    
    return sanitized 