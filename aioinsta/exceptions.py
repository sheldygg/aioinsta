class AioinstaException(BaseException):
    pass


class ChallengeRequired(AioinstaException):
    pass


class RateLimit(AioinstaException):
    pass


class IncorrectPassword(AioinstaException):
    pass


class ChallengeError(AioinstaException):
    pass
