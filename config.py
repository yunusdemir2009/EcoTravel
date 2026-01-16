"""
Configuration management for EcoTravel application.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration"""

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    FLASK_APP = os.getenv("FLASK_APP", "app.py")

    # Application Settings
    DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Ankara")
    POI_SEARCH_RADIUS_KM = int(os.getenv("POI_SEARCH_RADIUS_KM", "100"))
    MAX_TRAVEL_DAYS = int(os.getenv("MAX_TRAVEL_DAYS", "30"))
    MIN_BUDGET = int(os.getenv("MIN_BUDGET", "1000"))
    MAX_BUDGET = int(os.getenv("MAX_BUDGET", "1000000"))

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    # Rate Limiting
    RATELIMIT_ENABLED = os.getenv("RATELIMIT_ENABLED", "True").lower() == "true"
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "100 per hour")
    RATELIMIT_STORAGE_URL = os.getenv("RATELIMIT_STORAGE_URL", "memory://")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/ecotravel.log")


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""

    DEBUG = True
    TESTING = True
    RATELIMIT_ENABLED = False


# Config dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.getenv("FLASK_ENV", "development")
    return config.get(env, config["default"])
