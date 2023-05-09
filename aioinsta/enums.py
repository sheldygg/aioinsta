from enum import Enum


class ErrorTypes(str, Enum):
    CHALLENGE_REQUIRED = "checkpoint_challenge_required"
    RATE_LIMIT_ERROR = "rate_limit_error"
