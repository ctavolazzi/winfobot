from bot import Bot
from brain import Brain
import utils

class Central(Bot):
    DEFAULT_CONFIG = {
        'type': 'Central',
    }

    def __init__(self, config=None):
        super().__init__(config)
        self.config = self.DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)

        self.brain = Brain({'owner': self}) if not hasattr(self, 'brain') else self.brain
        self.logger = utils.setup_logger(self, 'DEBUG')
        self.logger.debug(f"Central {self.id} created")

    def handle(self, data, source):
        print(f"Central received data from {source.id}: {data}")
        self.brain.process(data)

    def broadcast(self, data, bots):
        for bot in bots:
            bot.receive(data, self)

    def receive(self, data, source):
        print(f"Central received data from Bot {source.id}: {data}")
        self.handle(data, source)
