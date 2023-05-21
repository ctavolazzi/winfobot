import threading
from port import Port
from state import State
from memory import Memory
from bot_behaviors import Behavior, BehaviorHandler, BehaviorFactory
from typing import Any, Dict, List, Union
from events import EventQueue, EventHandler
from events import MessageEvent, CommandEvent
from threaded_brain import ThreadedBrain
from formatters import BaseFormatter, JSONFormatter
from bot_handlers import MessageHandler, ConnectionHandler, GeneralHandler
from config import DefaultBotConfig
import asyncio
import utils
import pprint

class Bot:
    def __init__(self, config=None):
        self._initialize_default_config(DefaultBotConfig)
        self.setup_logger()
        self.lock = threading.Lock()
        self.name = utils.generate_name()
        self.type = self.__class__.__name__
        self.base_type = self.__class__.__name__
        self.formatter = JSONFormatter(self)
        self.q = EventQueue(EventHandler)

        # Bind the class instances
        self.port = Port({'owner': self}) if not hasattr(self, 'port') else self.port
        self.state = State({'owner': self}) if not hasattr(self, 'state') else self.state
        self.behavior = BehaviorHandler({'owner': self}) if not hasattr(self, 'behavior') else self.behavior
        self.memory = Memory({'owner': self}) if not hasattr(self, 'memory') else self.memory
        self.brain = ThreadedBrain({'owner': self}) if not hasattr(self, 'brain') else self.brain
        self.message_handler = MessageHandler({'owner': self}) if not hasattr(self, 'message_handler') else self.message_handler
        self.connection_handler = ConnectionHandler({'owner': self}) if not hasattr(self, 'connection_handler') else self.connection_handler

        if config:
            utils.update_config(self, config)

    def _initialize_default_config(self, config):
        self.config = config
        utils.run_default_config(self, config.DEFAULT_CONFIG)
        utils.verify_config(self, config.REQUIRED_KEYS)

    def setup_logger(self):
        logger_instance = utils.SingletonLogger(self.__class__.__name__)
        logger_instance.set_level(self._logger_level)
        self.logger = logger_instance.get_logger()

    async def handle_event(self, event):
        if isinstance(event, MessageEvent):
            await self.message_handler.handle_message(event.message, self)
        elif isinstance(event, CommandEvent):
            self.execute(event.command, *event.args)

    def execute(self, command, *args):
        try:
            if hasattr(self, command):
                getattr(self, command)(*args)
                self.logger.info(f"Executed command: {command}")
            else:
                self.logger.error(f"Unknown command: {command}")
        except TypeError as e:
            self.logger.error(f"Error executing command {command}: {str(e)}")

    async def add_event(self, event):
        self.q.add_event(event)

    async def process_events(self):
        while self.is_active:
            await self.q.process_events(self)

    def learn(self, behavior):
        if isinstance(behavior, Behavior):
            self._behaviors.append(behavior)
            self.logger.info(f"Learned new behavior: {type(behavior).__name__}")
        else:
            raise ValueError("The provided behavior must be an instance of the 'Behavior' class.")

    def set_formatter(self, formatter_class):
        if issubclass(formatter_class, BaseFormatter):
            self.formatter = formatter_class(self)
        else:
            self.logger.error('Formatter should be a subclass of BaseFormatter')
            raise TypeError("Formatter should be a subclass of BaseFormatter")

    async def send(self, data, destination):
        formatted_data = self.formatter.format(data)
        if isinstance(destination, Port):
            await destination.receive(formatted_data)
        elif isinstance(destination, Bot):
            await destination.port.receive(formatted_data)
        else:
            self.logger.error('Data destination should be an instance of Port or Bot')
            raise TypeError("Data destination should be an instance of Port or Bot")

    async def receive(self, data, source):
        if isinstance(source.port, Port):
            source = source.port.owner
            self.logger.info(f"Bot {self.id} received data from {source.id}: {data}")
            await self.message_handler.handle_message(data, self)
        else:
            raise TypeError("Data source should be an instance of Port")

    def get(self, attribute):
        return getattr(self, attribute, None)

    def identify(self):
        pprint.pprint(self.__dict__)

    def echo_data(self, data, source):
        # Echo back to source
        self.send(data, source)

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def __repr__(self):
        attributes = vars(self)
        lines = [f'Bot {self.id}']
        for attr, value in attributes.items():
            if attr.startswith('_') or attr in {'logger'}:
                continue
            elif attr in {'port', 'state', 'memory'}:
                value = repr(value)
            elif attr == 'lock':
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

    bot2 = Bot()
    print(f"Created new Bot with ID: {bot2.id}")
    assert bot2.port.id != None, "Bot's Port ID should not be None."
    assert bot2.port.owner.id == bot2.id, "Bot's Port owner should be the same as Bot's ID."

    print("\nConnecting Bot1 and Bot2...")
    bot1.port.connect(bot2.port)
    assert bot2.port in bot1.port.connections, "Bot2's port should be in Bot1's port connections."
    assert bot1.port in bot2.port.connections, "Bot1's port should be in Bot2's port connections."

    print("\nSetting Formatter for Bot1 and Bot2...")
    bot1.set_formatter(JSONFormatter)
    bot2.set_formatter(JSONFormatter)

    print("\nSending message from Bot1 to Bot2...")
    asyncio.run(bot1.send("Hello, Bot2!", bot2))

    print("\nPrinting Bot1 and Bot2 details...")
    print(bot1)
    print(bot2)

    print("\nDisconnecting Bot1 and Bot2...")
    bot1.port.disconnect(bot2.port)
    assert bot2.port not in bot1.port.connections, "Bot2's port should not be in Bot1's port connections after disconnecting."
    assert bot1.port not in bot2.port.connections, "Bot1's port should not be in Bot2's port connections after disconnecting."


if __name__ == "__main__":
    main()
