from bot import Bot
from port import Port
import utils
from message import Message
from controller import Controller

class Hub(Bot):
    DEFAULT_CONFIG = {
        'rules': {},
        'controller_model': 'default',
        # Add any other default configuration here
    }

    def __init__(self, config={}):
        super().__init__()
        self.run_default_config() # Always run this first
        self.logger = utils.setup_logger(self, 'DEBUG') # Always run this second

        self.port = Port({'owner': self})
        self.bots = set()
        self.config = self.DEFAULT_CONFIG.copy()
        self.config.update(config)

        self.controller = self.config.get('controller', None)
        if not isinstance(self.controller, Bot):
            raise TypeError("Controller should be an instance of Bot")

        self.rules = self.config.get('rules', {})
        if not isinstance(self.rules, dict):
            raise TypeError("Rules should be a dictionary")

    def run_default_config(self): # Always run this first in __init__
        self.config = self.DEFAULT_CONFIG.copy()
        for key, value in self.config.items():
            if not key.startswith('_') and not key in {'port'}: # Skip these attributes
                if callable(value): # If the value is a function, call it
                    self.config[key] = value() # This is useful for generating unique IDs
                elif isinstance(value, dict): # If the value is a dictionary, copy it
                    self.config[key] = value.copy() # This is useful for mutable default values
                elif isinstance(value, list): # This can also be engineered in the futute to help
                    self.config[key] = value.copy() # Scrup and process the setup of the hub
                elif isinstance(value, set): # In a different function somewhere
                    self.config[key] = value.copy() # For now, it lives here
                elif isinstance(value, tuple):
                    self.config[key] = value.copy()
                elif isinstance(value, str):
                    self.config[key] = value
                elif isinstance(value, int):
                    self.config[key] = value
                elif isinstance(value, float):
                    self.config[key] = value
                elif isinstance(value, bool):
                    self.config[key] = value
                elif isinstance(value, type(None)):
                    self.config[key] = value
                elif isinstance(value, object):
                    self.config[key] = value
                elif isinstance(value, type):
                    self.config[key] = value
                else:
                    self.config[key] = value

    def __repr__(self):
        attributes = vars(self)
        lines = [f'Hub {self.id}']
        for attr, value in attributes.items():
            if attr in {'id', '_password'}:  # Skip these attributes
                continue
            if attr == 'modules':  # For modules, we want to list the module names only
                value = ', '.join(value.keys())
            elif attr in {'port', 'state', 'memory'}:  # Use repr(value) for detailed information
                value = repr(value)
            elif attr == 'logger':  # For logger, we want to display its level
                value = value.level
            elif attr == 'lock':  # For lock, we want to display its state
                value = 'locked' if value.locked() else 'unlocked'
            elif attr == 'bots':  # For bots, we want to display the number of bots
                value = len(value)
            lines.append(f'{attr}: {value}')
        return '\n'.join(lines)

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
            self.port.send(bot, data)

    def receive(self, data, source):
        if not isinstance(source, Bot):
            raise TypeError("Data source should be an instance of Bot")

        if self._check_rules(source):
            self.controller.handle(data, source)
        else:
            print(f"Bot {source.id} is not following the rules. Data not accepted.")

    def __str__(self):
        return f"Hub {self.port.address}"

if __name__ == '__main__':
    # Create a controller bot for the hub
    controller_bot = Bot({'name': 'Central', 'type': 'Controller'})

    # Create a hub
    hub = Hub({'controller': controller_bot})

    # Create two other bots
    bot1 = Bot()
    bot2 = Bot()

    # Test adding bots to the hub
    hub.add_bot(bot1)
    hub.add_bot(bot2)

    # The hub should now have two bots
    assert len(hub.bots) == 2, "Bots were not added correctly"

    # Test broadcasting data
    hub.broadcast("Test data")
    # Both bots should have received the data
    assert bot1.memory.get_memory()['received_data'][-1] == "Test data", "Bot1 did not receive the data"
    assert bot2.memory.get_memory()['received_data'][-1] == "Test data", "Bot2 did not receive the data"

    # Test receiving data
    hub.receive("Test data from bot1", bot1)
    # The controller should have handled the data
    assert controller_bot.memory.get_memory()['received_data'][-1] == "Test data from bot1", "Controller did not receive the data"

    # Test removing a bot
    hub.remove_bot(bot1)
    # The hub should now have one bot
    assert len(hub.bots) == 1, "Bot1 was not removed correctly"

    print("All tests passed.")
