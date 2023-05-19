import uuid
import threading
import pprint
from port import Port
from state import State
from memory import Memory
import datetime
from utils import setup_logger
import random
import string
# from haikunator import Haikunator # for generating random names but the import isn't working

class Bot:
    """
    The Bot class represents a bot with the ability to communicate via a port.

    Attributes:
    id (str): a unique identifier for the bot.
    port (Port): a Port object for the bot to communicate through.
    """

    def __init__(self, config=None):
        self.run_default_config() # Always run this first

        if config:
            self.run_config(config) # Run the config if it exists

        self.state = State() if not hasattr(self, 'state') else self.state
        self.memory = Memory() if not hasattr(self, 'memory') else self.memory

        self.logger = setup_logger(self, 'DEBUG')
        self.logger.info(f'Initialized {self.__class__.__name__} {self.id} with config {config}')

        self.port = Port({'owner': self}) if not hasattr(self, 'port') else self.port
        self.lock = threading.Lock()

    def run_default_config(self):
        # Set default values for the bot
        self.id = str(uuid.uuid4())
        self.name = self.generate_name()
        self.type = self.__class__.__name__
        self.config = {'id': self.id, 'name': self.name, 'type': self.type}
        self._base_type = self.__class__.__name__
        self._created_at = datetime.datetime.now()
        self._updated_at = datetime.datetime.now()
        self._parent_id = None
        self._restricted_config_keys = {'id', 'port', 'state', 'memory', 'logger', 'lock'} # These keys cannot be changed

    def run_config(self, config):
        for key, value in config.items():
            if key not in self._restricted_config_keys and not key.startswith('_'): # Skip these attributes
                if callable(value):
                    setattr(self, key, value(self))
                else:
                    setattr(self, key, value)
            else:
                self.logger.warning(f"Restricted key {key} in Bot config. Skipping.")
        self._updated_at = datetime.datetime.now()
        self.config = config
        self.logger.info(f"Updated config for {self.__class__.__name__} {self.id} with {config}")

    def generate_name(self):
        return self.__class__.__name__ + str(random.choices(string.ascii_lowercase, k=5)) + str(random.randint(1000,9999))

    def attempt_connection(self, port):
        if isinstance(port, Port):
            # logic for handling port connections
            pass
        else:
            raise TypeError(f'Expected a Port object, but got {type(port).__name__}')

    def disconnect(self, port):
        if isinstance(port, Port):
            self.port.disconnect(port)
        else:
            raise TypeError(f'Expected a Port object, but got {type(port).__name__}')

    def get(self, attribute):
        if hasattr(self, attribute):
            return getattr(self, attribute)
        else:
            raise AttributeError(f"{attribute} not found in bot attributes")

    def remember(self, item):
        self.memory.remember(item)

    def recall(self, item):
        return self.memory.recall(item)

    def forget(self, item):
        self.memory.forget(item)

    def identify(self):
       pprint.pprint(self.__dict__)

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def __repr__(self):
        attributes = vars(self)
        lines = [f'Bot {self.id}']
        for attr, value in attributes.items():
            if attr.startswith('_') or attr in {'logger'}:  # Skip these attributes
                continue
            elif attr in {'port', 'state', 'memory'}:  # Use repr(value) for detailed information
                value = repr(value)
            elif attr == 'lock':  # For lock, we want to display its state in a verbose way
                value = 'Locked: True' if value.locked() else 'Locked: False'
            lines.append(f'{attr}: {value}')
        return '\n'.join(lines)


    def __str__(self):
        return f'Bot {self.id} \n Port {self.port.get_address()} \n State: {self.state} \n Config: {self.config} \n Connections: {self.port.connections} \n Memory: {self.memory} \n Lock: {self.lock} \n Logger: {self.logger} \n '

def main():
    # Create a new bot with default settings
    bot1 = Bot()
    print(f"Created new Bot with ID: {bot1.id}")

    # Test Port creation and owner setting
    assert bot1.port.id != None, "Bot's Port ID should not be None."
    assert bot1.port.owner.id == bot1.id, "Bot's Port owner should be the same as Bot's ID."

    # Test if changing the owner of Port is restricted
    try:
        bot1.port.owner = Bot()
    except AttributeError:
        print("Successfully restricted Port's owner from being changed.")

    # Test Port's address
    assert isinstance(bot1.port.address, str), "Bot's Port address should be a string."

    # Test Bot's memory
    bot1.remember("item1")
    assert any(item.data == "item1" for item in bot1.memory.get_memory()['working_memory']), "Bot's memory should contain the remembered item."


    # Test Bot's state
    assert isinstance(bot1.state, State), "Bot's state should be an instance of State."
    bot1.state.update({"name": "NewState"})
    assert bot1.state.state_dict['name'] == "NewState", "Bot's state should update correctly."

    # Test Bot's connections
    assert isinstance(bot1.port.connections, set), "Bot's connections should be a set."
    bot2 = Bot()
    bot1.port.connect(bot2.port)
    assert bot2.port in bot1.port.connections, "Bot's connections should include the connected port."

    # Test Bot's disconnection
    bot1.port.disconnect(bot2.port)
    assert bot2.port not in bot1.port.connections, "Bot's connections should not include the disconnected port."

if __name__ == '__main__':
    main()