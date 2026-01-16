"""
Logging configuration for EcoTravel application.
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger


def setup_logging(app):
    """Configure logging for the application"""

    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Get log level from config
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO"))
    log_file = app.config.get("LOG_FILE", "logs/ecotravel.log")

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)

    # File Handler with rotation
    file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=10)  # 10MB per file
    file_handler.setLevel(log_level)
    
    # JSON formatter for structured logging
    json_formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d"
    )
    file_handler.setFormatter(json_formatter)

    # Configure Flask app logger
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)

    # Log startup
    app.logger.info("EcoTravel application started", extra={"environment": app.config.get("ENV", "development")})

    return app.logger


class RequestLogger:
    """Middleware for logging HTTP requests"""

    def __init__(self, app):
        self.app = app

    def log_request(self, request, response, duration_ms):
        """Log request details"""
        self.app.logger.info(
            "HTTP Request",
            extra={
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "ip": request.remote_addr,
                "user_agent": request.user_agent.string if request.user_agent else None,
            },
        )
