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

class HandlerFactory(Handler):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.handlers = self.create_handlers(config)

    @staticmethod
    def create_handlers(config=None):
        # Create default handler instances
        handlers = {
            'CommandHandler': CommandHandler(),
            'MessageHandler': MessageHandler(),
            'GeneralHandler': GeneralHandler(),
            'EventHandler': EventHandler(),
            'MessageEventHandler': MessageEventHandler(),
            'CommandEventHandler': CommandEventHandler(),
        }

        if config is not None:
            # If there's a custom config, extend the default handler list with the custom ones.
            for handler_class, handler_config in config.items():
                handlers[handler_class] = handler_class(handler_config)

        return handlers



class TypeHandler(Handler):
    @staticmethod
    @abstractmethod
    def can_handle(type: str) -> bool:
        raise NotImplementedError("This method should be overridden in subclass")

    @abstractmethod
    def handle(self, data: Any):
        raise NotImplementedError("This method should be overridden in subclass")

class CommandHandler(TypeHandler):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)

    @staticmethod
    def can_handle(type: str) -> bool:
        return type == 'CommandEvent'

    def handle(self, event: CommandEvent):
        self.logger.info(f"Command Event Received. Command: {event.payload}")
        event._log.add_entry("CommandEvent was processed.")

class MessageHandler(TypeHandler):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)

    @staticmethod
    def can_handle(type: str) -> bool:
        return type == 'MessageEvent'

    def handle(self, event: MessageEvent):
        assert isinstance(event, MessageEvent), "Event must be an instance of MessageEvent."
        self.logger.info(f"Message Event Received. Content: {event.payload}")
        event._log.add_entry("MessageEvent was processed.")

import logging

class GeneralHandler(TypeHandler):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def can_handle(type: str) -> bool:
        return True  # Always return True

    def handle(self, event: Event):
        self.logger.info(f"GeneralHandler received an event of type: {type(event).__name__}")
        return self.handle_stuff(event.content)

    def handle_stuff(self, stuff):
        handler_name = f"_handle_{type(stuff).__name__}"
        handler = getattr(self, handler_name, self._handle_default)
        return handler(stuff)

    # Default handler if no specific handler method exists
    def _handle_default(self, stuff):
        self.logger.info(f"Received an object of type {type(stuff).__name__} in GeneralHandler")
        return f"GeneralHandler received: {stuff}"

    def _handle_str(self, stuff):
        self.logger.info(f"Received a string in GeneralHandler")
        return f"GeneralHandler received a string: {stuff}"

    def _handle_dict(self, stuff):
        self.logger.info(f"Received a dictionary in GeneralHandler")
        return f"GeneralHandler received a dictionary: {stuff}"

    def _handle_list(self, stuff):
        self.logger.info(f"Received a list in GeneralHandler")
        return f"GeneralHandler received a list: {stuff}"

    def _handle_int(self, stuff):
        self.logger.info(f"Received an integer in GeneralHandler")
        return f"GeneralHandler received an integer: {stuff}"

    def _handle_float(self, stuff):
        self.logger.info(f"Received a float in GeneralHandler")
        return f"GeneralHandler received a float: {stuff}"

    def _handle_datetime(self, stuff):
        self.logger.info(f"Received a datetime in GeneralHandler")
        return f"GeneralHandler received a datetime: {stuff}"

    def _handle_Event(self, stuff):
        self.logger.info(f"Received an Event in GeneralHandler")
        return f"GeneralHandler received an Event: {stuff}"

    def _handle_TypeHandler(self, stuff):
        self.logger.info(f"Received a TypeHandler in GeneralHandler")
        return f"GeneralHandler received a TypeHandler: {stuff}"

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