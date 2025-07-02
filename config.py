import os
from typing import Optional

class DatabaseConfig:
    """Database configuration settings"""
    
    # MongoDB settings
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "resume_parser_db")
    
    # Collections
    RESUMES_COLLECTION: str = "resumes"
    INTERVIEW_SESSIONS_COLLECTION: str = "interview_sessions"
    USERS_COLLECTION: str = "users"
    
    # Connection settings
    MAX_CONNECTIONS: int = int(os.getenv("MAX_CONNECTIONS", "100"))
    CONNECTION_TIMEOUT: int = int(os.getenv("CONNECTION_TIMEOUT", "30000"))  # milliseconds
    
    @classmethod
    def get_mongodb_url(cls) -> str:
        """Get MongoDB connection URL"""
        return cls.MONGODB_URL
    
    @classmethod
    def get_database_name(cls) -> str:
        """Get database name"""
        return cls.DATABASE_NAME

class AppConfig:
    """Application configuration settings"""
    
    # API settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # File upload settings
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx", ".doc", ".txt"]
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Environment-specific configurations
class DevelopmentConfig(DatabaseConfig, AppConfig):
    """Development environment configuration"""
    DEBUG = True
    MONGODB_URL = "mongodb://localhost:27017/"

class ProductionConfig(DatabaseConfig, AppConfig):
    """Production environment configuration"""
    DEBUG = False
    # Override with production MongoDB URL
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")

class TestingConfig(DatabaseConfig, AppConfig):
    """Testing environment configuration"""
    DEBUG = True
    DATABASE_NAME = "resume_parser_test_db"
    MONGODB_URL = "mongodb://localhost:27017/"

# Configuration factory
def get_config(env: Optional[str] = None) -> DatabaseConfig:
    """Get configuration based on environment"""
    env = env or os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()

# Default configuration
config = get_config()