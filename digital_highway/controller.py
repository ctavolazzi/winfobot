from bot import Bot

class Controller(Bot):
    DEFAULT_CONFIG = {
        'name': 'Controller',
        'type': 'Controller',
    }

    def __init__(self, config={}):
        super().__init__(config)
        self.config = self.DEFAULT_CONFIG.copy()
        self.config.update(config)

    def handle(self, data, source):
        # Override the handle method if necessary
        super().handle(data, source)
