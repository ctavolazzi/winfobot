from bot import Bot
from port import Port
import utils
from message import Message
import uuid

class Hub():
    DEFAULT_CONFIG_SELF = {
        'type': lambda self: self.__class__.__name__,
        '_base_type': lambda self: self.__class__.__name__,
    }

    DEFAULT_CONFIG = {
        'rules': lambda: {},
        'id': lambda: str(uuid.uuid4()),
        'address': lambda: str(uuid.uuid4()),
        'connections': lambda: set(),
        'owner': lambda: None,
        '_hashed_password': lambda: hash('password'),
        '_restricted_config_keys': lambda: {'id', 'address', 'connections', 'lock'},
    }

    def __init__(self, config=None):
        self.run_default_config()
        self.logger = utils.setup_logger(self, 'DEBUG')

        self.port = Port({'owner': self})
        self.bots = set()

        if config:
            self.run_config(config)

        if not isinstance(self.rules, dict):
            raise TypeError("Rules should be a dictionary")

        self.logger.info(f'Initialized {self.__class__.__name__} {self.id} with config {config}')

    def run_default_config(self):
        for key, default_value_func in self.DEFAULT_CONFIG.items():
            if callable(default_value_func):
                setattr(self, key, default_value_func())

        for key, default_value_func in self.DEFAULT_CONFIG_SELF.items():
            setattr(self, key, default_value_func(self))

    # rest of your code ...

    def add_bot(self, bot):
        if not isinstance(bot, Bot):
            raise TypeError("Only instances of Bot can be added to the hub")

        if self._check_rules(bot):
            self.bots.add(bot)
            self.port.connect(bot.port)
            print(f"Bot {bot.id} connected to the hub.")
        else:
            print(f"Bot {bot.id} does not follow the rules of the hub and cannot be connected.")

    def remove_bot(self, bot):
        if not isinstance(bot, Bot):
            raise TypeError("Only instances of Bot can be removed from the hub")

        if bot in self.bots:
            self.bots.remove(bot)
            self.port.disconnect(bot.port)
            print(f"Bot {bot.id} disconnected from the hub.")
        else:
            print(f"Bot {bot.id} is not connected to the hub.")

    def _check_rules(self, bot):
        # TODO: implement rule checking
        return True

    def broadcast(self, data):
        if not self.bots:
            raise RuntimeError("No bots connected to the hub to broadcast data")
        for bot in self.bots:
            bot.receive(data)

    def receive(self, data, source_port):
        if not isinstance(source_port, Port):
            raise TypeError("Data source should be an instance of Port")

        source = source_port.owner
        if self._check_rules(source): # Assuming 'owner' is a bot.
            self.handle(data, source)
        else:
            print(f"Bot {source.id} is not following the rules. Data not accepted.")

    def handle(self, data, source):
        print(f"Hub received data from {source.id}: {data}")

    def __str__(self):
        return f"Hub {self.port.address}"

if __name__ == '__main__':
    # Create a hub
    hub = Hub()

    # Create two bots and connect them to the hub
    bot1 = Bot()
    bot2 = Bot()
    hub.add_bot(bot1)
    hub.add_bot(bot2)

    # The hub should now have two bots
    assert len(hub.bots) == 2, "Bots were not added correctly"

    # Test broadcasting data
    hub.broadcast("Test data")
    # Both bots should have received the data

    # Test receiving data
    hub.receive("Test data from bot1", bot1.port)
    # The hub should have handled the data

    # Test removing a bot
    hub.remove_bot(bot1)
    # The hub should now have one bot
    assert len(hub.bots) == 1, "Bot1 was not removed correctly"

    print("All tests passed.")