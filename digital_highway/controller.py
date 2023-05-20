from bot import Bot
import utils

class Controller(Bot):
    DEFAULT_CONFIG_SELF = {
        'type': lambda self: self.__class__.__name__,
    }

    DEFAULT_CONFIG = {}

    def __init__(self, config=None):
        self.run_default_config() # Always run this first
        self.logger = utils.setup_logger(self, 'DEBUG') # Always run this second

        if config:
            self.run_config(config) # Run the config if it exists

    def run_default_config(self):
        super().run_default_config()
        for key, default_value_func in self.DEFAULT_CONFIG_SELF.items():
            setattr(self, key, default_value_func(self))
        for key, default_value_func in self.DEFAULT_CONFIG.items():
            setattr(self, key, default_value_func())

    # ... rest of your code ...

    def handle(self, data, source):
        print(f"Controller received data from {source.id}: {data}")
        return data

    def broadcast(self, data, bots):
        for bot in bots:
            bot.receive(data)

    def receive(self, data, source):
        print(f"Controller received data from Bot {source.id}: {data}")
