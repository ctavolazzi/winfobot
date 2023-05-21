import uuid
import threading
import pprint
from port import Port
from state import State
from memory import Memory
import datetime
import utils
import random
import string
from brain import Brain
from bot_behaviors import Behavior, BehaviorFactory

class ThreadedBrain(Brain):
    def __init__(self, owner):
        super().__init__(owner)
        self.thread = threading.Thread(target=self.thinking)
        self.stop_event = threading.Event()

    def start_thinking(self):
        self.thread.start()

    def stop_thinking(self):
        self.stop_event.set()
        self.thread.join()

    def thinking(self):
        while not self.stop_event.is_set():
            # Your thinking logic goes here

            pass

class MessageHandler:
    def handle_message(self, message, bot):
        # Implement message handling logic here
        pass

class ConnectionHandler:
    def handle_connection(self, connection, bot):
        # Implement connection handling logic here
        pass

class Bot:
    _REQUIRED_CONFIG_KEYS = ['id', 'inventory', 'logger', 'lock', 'port', 'state', 'memory', 'brain']

    _DEFAULT_CONFIG = {
        'id': lambda: str(uuid.uuid4()),
        'inventory': lambda: {'items': []},
        'lock': lambda: threading.Lock(),
        '_created_at': lambda: datetime.datetime.now(),
        '_updated_at': lambda: datetime.datetime.now(),
        '_parent': lambda: None,
        '_logger_level': 'DEBUG',
        '_restricted_config_keys': lambda: {'id', 'port', 'state', 'memory', 'logger', 'lock'},
        'is_thinking': False,
        'is_updating': False,
        'is_active': True,
        'has_controller': False,
    }

    def __init__(self, config=None):
        self._initialize_default_config()
        self._initialize_default_behaviors()
        self.setup_logger()

        # Set up the bot's self referential config
        self.name = self.generate_name()
        self.type = self.__class__.__name__
        self._base_type = self.__class__.__name__

        # Bind the bot to its components
        self.port = Port({'owner': self}) if not hasattr(self, 'port') else self.port
        self.state = State({'owner': self}) if not hasattr(self, 'state') else self.state
        self.memory = Memory({'owner': self}) if not hasattr(self, 'memory') else self.memory
        self.brain = ThreadedBrain({'owner': self}) if not hasattr(self, 'brain') else self.brain

        # Set up the handlers
        self.message_handler = MessageHandler()
        self.connection_handler = ConnectionHandler()

        if config:
            utils.update_config(self, config)

        self.logger.info(f'Initialized {self.__class__.__name__} {self.id} with config {config}')

    # Config methods
    def _initialize_default_config(self):
        utils.run_default_config(self, self._DEFAULT_CONFIG)
        utils.verify_config(self, self._REQUIRED_CONFIG_KEYS)

    def _initialize_default_behaviors(self):
        self._behaviors = BehaviorFactory.create_behaviors()


    def setup_logger(self):
        logger_instance = utils.SingletonLogger(self.__class__.__name__)  # Getting the logger instance
        logger_instance.set_level(self._logger_level)  # Setting the log level
        self.logger = logger_instance.get_logger()  # Getting the logger object

    # Handlers
    def handle(self, data, source):
        self.logger.debug(f"Handling data: {data}")
        try:
            for behavior in self._behaviors:
                if behavior.can_handle(data):
                    behavior.handle(data)
                    break
        except Exception as e:
            self.logger.error(f"Error while handling data: {str(e)}")
        else:
            source.port.send(self, data)

    # Define the function for parsing data
    def _handle_data(self, data, source):
        try:
            for behavior in self._behaviors:
                if behavior.can_handle(data):
                    behavior.handle(data)
                    break
        except Exception as e:
            self.logger.error(f"Error while handling data: {str(e)}")
        else:
            source.port.send(self, data)

    # Updaters
    def update_config(self, config):
        for key, value in config.items():
            if key not in self._restricted_config_keys and not key.startswith('_'):
                if callable(value):
                    setattr(self, key, value(self))
                else:
                    setattr(self, key, value)
            else:
                self.logger.warning(f"Restricted key {key} in Bot config. Skipping.")
        self._updated_at = datetime.datetime.now()
        self.logger.info(f"Updated config for {self.__class__.__name__} {self.id} with {config}")

    # State methods
    def update_state(self, state):
        self.state.update(state)

    # Memory methods
    def remember(self, item):
        self.memory.remember(item)

    def recall(self, item):
        return self.memory.recall(item)

    def forget(self, item):
        self.memory.forget(item)

    # Generator methods
    def generate_name(self):
        return self.__class__.__name__ + ''.join(random.choices(string.ascii_lowercase, k=5)) + str(random.randint(1000,9999))

    # Connection methods
    def attempt_connection(self, port):
        if isinstance(port, Port):
            self.port.connect(port)
            self.connection_handler.handle_connection(port, self)
        else:
            self.logger.error('Expected a Port object, but got {type(port).__name__}')
            raise TypeError(f'Expected a Port object, but got {type(port).__name__}')

    def disconnect(self, port):
        if isinstance(port, Port):
            self.port.disconnect(port)
        else:
            self.logger.error('Expected a Port object, but got {type(port).__name__}')
            raise TypeError(f'Expected a Port object, but got {type(port).__name__}')

    # Send and receive methods
    def send(self, data, destination):
        if isinstance(destination, Port):
            destination.receive(data, self.port)
        elif isinstance(destination, Bot):
            destination.port.receive(data, self.port)
        else:
            self.logger.error('Data destination should be an instance of Port or Bot')
            raise TypeError("Data destination should be an instance of Port or Bot")


    def receive(self, data, source_port):
        if isinstance(source_port, Port):
            source = source_port.owner
            self.logger.info(f"Bot {self.id} received data from {source.id}: {data}")
            self.message_handler.handle_message(data, self)
        else:
            raise TypeError("Data source should be an instance of Port")

    def attempt_connection(self, port):
        if isinstance(port, Port):
            self.port.connect(port)
            self.connection_handler.handle_connection(port, self)
        else:
            self.logger.error('Expected a Port object, but got {type(port).__name__}')
            raise TypeError(f'Expected a Port object, but got {type(port).__name__}')

    # Getters and setters
    def get(self, attribute):
        try:
            return getattr(self, attribute)
        except AttributeError:
            self.logger.error(f"{attribute} not found in bot attributes")

    # Debugging methods
    def identify(self):
       pprint.pprint(self.__dict__)

    # Handlers
    def handle(self, data, source):
        # Here is where you could use your handle_string, handle_dict and handle_list methods.
        # Just as an example:
        if isinstance(data, str):
            self._handle_string(data, source)
        elif isinstance(data, dict):
            self._handle_dict(data, source)
        elif isinstance(data, list):
            self._handle_list(data, source)
        else:
            print(f"Data type {type(data).__name__} not recognized by bot {self.id} handle func.")

    # Define the functions for parsing different types of data
    def _handle_string(self, data, source):
        # Here you might do something with the data...
        # then echo back to source
        source.port.send(self, data)

    def _handle_dict(self, data, source):
        # Here you might do something with the data...
        # then echo back to source
        source.port.send(self, data)

    def _handle_list(self, data, source):
        # Here you might do something with the data...
        # then echo back to source
        source.port.send(self, data)

    # Magic methods
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
    bot1 = Bot()
    print(f"Created new Bot with ID: {bot1.id}")

    assert bot1.port.id != None, "Bot's Port ID should not be None."
    assert bot1.port.owner.id == bot1.id, "Bot's Port owner should be the same as Bot's ID."

    try:
        bot1.port.owner = Bot()
    except AttributeError:
        print("Successfully restricted Port's owner from being changed.")

    assert isinstance(bot1.port.address, str), "Bot's Port address should be a string."

    bot1.remember("item1")
    assert any(item.data == "item1" for item in bot1.memory.get_memory()['working_memory']), "Bot's memory should contain the     remembered item."

    assert isinstance(bot1.state, State), "Bot's state should be an instance of State."
    bot1.state.update({"name": "NewState"})
    assert bot1.state.state_dict['name'] == "NewState", "Bot's state should update correctly."

    assert isinstance(bot1.port.get_connections(), set), "Bot's connections should be a set."
    bot2 = Bot()
    bot1.attempt_connection(bot2.port)
    assert bot2.port in bot1.port.get_connections(), "Bot's connections should include the connected port."

    bot1.disconnect(bot2.port)
    assert bot2.port not in bot1.port.get_connections(), "Bot's connections should not include the disconnected port."

    bot1.send({"type": "message", "content": "Hello, bot2!"}, bot2)
    bot1.send({"type": "command", "content": "Goodbye, bot2!"}, bot2)

if __name__ == '__main__':
    main()
