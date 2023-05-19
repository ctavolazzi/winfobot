from bot import Bot
from port import Port
import utils

class Hub(Bot):
    DEFAULT_CONFIG = {
        'rules': {},
        'controller': None,
        # Add any other default configuration here
    }

    def __init__(self, config={}):
        self.port = Port({'owner': self})
        self.bots = set()
        self.config = self.DEFAULT_CONFIG.copy()
        self.config.update(config)
        self.logger = utils.setup_logger(self, 'DEBUG')

        self.controller = self.config.get('controller', None)
        if not isinstance(self.controller, Bot):
            raise TypeError("Controller should be an instance of Bot")

        self.rules = self.config.get('rules', {})
        if not isinstance(self.rules, dict):
            raise TypeError("Rules should be a dictionary")

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
        pass

    def broadcast(self, data):
        if not self.bots:
            raise RuntimeError("No bots connected to the hub to broadcast data")

        for bot in self.bots:
            self.port.send(data, bot.port)

    def receive(self, data, source):
        if not isinstance(source, Bot):
            raise TypeError("Data source should be an instance of Bot")

        if self._check_rules(source):
            self.controller.handle(data, source)
        else:
            print(f"Bot {source.id} is not following the rules. Data not accepted.")

    def __str__(self):
        return f"Hub {self.port.address}"
