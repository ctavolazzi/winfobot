from bot import Bot
import utils

class Controller(Bot):
    DEFAULT_CONFIG = {
        'type': 'Controller',
    }

    def __init__(self, config=None):
        super().__init__(config)
        self.config = self.DEFAULT_CONFIG.copy()
        self.config.update(config)

        self.logger = utils.setup_logger(self, 'DEBUG')
        self.logger.debug(f"Controller {self.id} created")

    def handle(self, data, source):
        print(f"Controller received data from {source.id}: {data}")
        return data

    def broadcast(self, data, bots):
        for bot in bots:
            bot.receive(data)

    def receive(self, data, source):
        print(f"Controller received data from Bot {source.id}: {data}")
