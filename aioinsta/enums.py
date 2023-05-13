from enum import Enum


class ErrorTypes(str, Enum):
    CHALLENGE_REQUIRED = "challenge_required"
    RATE_LIMIT_ERROR = "rate_limit_error"
