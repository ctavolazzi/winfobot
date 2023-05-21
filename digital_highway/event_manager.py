# event_manager.py
from event_queue import EventQueue
from event_handlers import MessageEventHandler, CommandEventHandler
from events import MessageEvent, CommandEvent

class EventManager:
    def __init__(self):
        self.event_queue = EventQueue()
        self.register_handlers()

    def register_handlers(self):
        self.event_queue.register_handler(MessageEvent, MessageEventHandler())
        self.event_queue.register_handler(CommandEvent, CommandEventHandler())

    # ... rest of your code ...
