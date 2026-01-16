"""
Custom exceptions for EcoTravel application.
"""


class EcoTravelException(Exception):
    """Base exception for EcoTravel"""

    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["error"] = self.message
        rv["status_code"] = self.status_code
        return rv


class ValidationError(EcoTravelException):
    """Raised when input validation fails"""

    status_code = 400


class ResourceNotFoundError(EcoTravelException):
    """Raised when a requested resource is not found"""

    status_code = 404


class ConfigurationError(EcoTravelException):
    """Raised when there's a configuration problem"""

    status_code = 500


class RateLimitExceeded(EcoTravelException):
    """Raised when rate limit is exceeded"""

    status_code = 429
