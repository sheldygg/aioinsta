from aioinsta.login import Login


class Client(Login):
    def __init__(self, settings: dict | None = None):
        if settings is None:
            settings = {}
        super().__init__(settings)
        self.init()
