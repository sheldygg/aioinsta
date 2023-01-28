from .methods import LoginClient, MediaClient, UserClient


class InstagramClient(MediaClient, LoginClient, UserClient):
    def __init__(self, settings: dict = {}) -> None:
        super().__init__()
        self.settings = settings
        self.before_start()
