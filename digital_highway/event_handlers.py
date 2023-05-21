
from abc import ABC, abstractmethod
from typing import Dict, Type, List, Any
from datetime import datetime
from events import Event, MessageEvent, CommandEvent
from utils import generate_unique_id, setup_logger

class EventLog:
    def __init__(self):
        self.history = []

    def add_entry(self, entry):
        self.history.append((datetime.now(), entry))

class Event(ABC):
    def __init__(self, payload: str):
        self._id = generate_unique_id()
        self._payload = payload
        self._timestamp = datetime.now()
        self._log = EventLog()
        self._metadata: Dict[str, Any] = {}

    @property
    def log(self):
        return self._log.history

class EventHandler(ABC):
    def __init__(self):
        self.id = generate_unique_id()
        self.logger = setup_logger(self)
        self.handlers: Dict[str, Type[EventHandler]] = {
            "MessageEvent": MessageEventHandler,
            "CommandEvent": CommandEventHandler
        }

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
