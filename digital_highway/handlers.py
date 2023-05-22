import functools
from abc import ABC, abstractmethod
from typing import Dict, Type, List, Any
from datetime import datetime
from events import Event, MessageEvent, CommandEvent
from utils import generate_unique_id, setup_logger, run_config

class Handler(ABC):
    def __init__(self, config: Dict[str, Any] = None):
        self.id = generate_unique_id()
        self._config = config
        self._logger = setup_logger(self)

        if config:
            run_config(self, config)

    @abstractmethod
    def handle_event(self, event: Event, bot):
        pass

class MessageHandler(Handler):
    """Handles message events"""
    def __init__(self, config):
        super().__init__(config)
        self.owner = config['owner']

    def handle_event(self, message, bot):
        """Handles a single message"""
        ...

class ConnectionHandler(Handler):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.owner = config['owner']

    def handle_event(self, connection, bot):
        # TODO: Implement connection handling logic here
        if connection not in bot.port.get_connections():
            bot.logger.warning(f"Received a connection from an unknown source: {connection.owner}")
            bot.port.connect(connection)
        else:
            bot.logger.info(f"Received a connection from {connection.owner}")

class GeneralHandler(Handler):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)

    @functools.singledispatchmethod
    def handle_stuff(self, stuff):
        print(f"Received an object of type {type(stuff).__name__} in GeneralHandler: {stuff}")
        # Default handling logic for other types of data goes here
        return f"GeneralHandler received: {stuff}"

    @handle_stuff.register
    def _(self, stuff: str):
        print(f"Received a string in GeneralHandler: {stuff}")
        # Further logic for handling string goes here
        return f"GeneralHandler received a string: {stuff}"

    @handle_stuff.register
    def _(self, stuff: dict):
        print(f"Received a dictionary in GeneralHandler: {stuff}")
        # Further logic for handling dictionary goes here
        return f"GeneralHandler received a dictionary: {stuff}"

class EventHandler(Handler):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        if not hasattr(self, 'handlers'):
            self.handlers = {}

    def handle(self, event: Event):
        if not isinstance(event, Event):
            raise TypeError("Provided event is not an instance of the Event class.")

        event_type = type(event).__name__
        if event_type not in self.handlers:
            self.logger.info(f"Creating new handler for event type {event_type}")
            new_handler_class = type(f"{event_type}Handler", (EventHandler,), {})
            new_handler_class.handle = self.generate_handle_method(event_type)
            self.handlers[event_type] = new_handler_class

        handler = self.handlers[event_type]()
        handler.handle(event)

        event._log.add_entry(f"Event handled by {type(handler).__name__}")

    def generate_handle_method(self, event_type: str):
        def handle(self, event):
            self.logger.info(f"Handling {event_type}. Content: {event.payload}")
        return handle

class MessageEventHandler(EventHandler):
    def handle(self, event: MessageEvent):
        assert isinstance(event, MessageEvent), "Event must be an instance of MessageEvent."
        self.logger.info(f"Message Event Received. Content: {event.payload}")
        event._log.add_entry("MessageEvent was processed.")

class CommandEventHandler(EventHandler):
    def handle(self, event: CommandEvent):
        assert isinstance(event, CommandEvent), "Event must be an instance of CommandEvent."
        self.logger.info(f"Command Event Received. Command: {event.payload}")
        event._log.add_entry("CommandEvent was processed.")