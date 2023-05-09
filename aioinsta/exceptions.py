class AioinstaException(BaseException):
    pass


class ChallengeRequired(AioinstaException):
    pass


class RateLimit(AioinstaException):
    pass
