# port.py
import asyncio
import uuid
import utils
from message import Message
import bcrypt
import secrets
from errors import InvalidDestinationError
from event_queue import EventQueue
from managers import ConnectionManager, MessageManager

class Port:
    def __init__(self, event_queue: EventQueue = None, config=None):
        self.id = str(uuid.uuid4())
        self.address = str(uuid.uuid4())
        self.lock = asyncio.Lock()
        self.event_queue = event_queue if event_queue else EventQueue()
        self.connection_manager = ConnectionManager(self)
        self.message_manager = MessageManager(self)
        self.logger = utils.setup_logger(self)
        self._initialize_handlers()
        if config:
            utils.update_config(self, config)

    def _initialize_handlers(self):
        self._handlers = HandlerFactory.create_handlers(self)

    async def handle(self, event):
        self.logger.debug(f"Handling event: {event}")
        try:
            await self.event_queue.add_event(event)
        except Exception as e:
            self.logger.error(f"Error while handling event: {str(e)}")

    async def connect(self, target):
        async with self.lock:  # Acquire the lock
            await self.connection_manager.connect(target)

    async def disconnect(self, target):
        async with self.lock:  # Acquire the lock
            await self.connection_manager.disconnect(target)

    async def send(self, content, destinations):
        await self.message_manager.send(content, destinations)

    async def receive(self, data):
        await self.message_manager.receive(data)

    async def broadcast(self, content):
        for destination in self.connection_manager.connections:
            await self.message_manager.send(content, destination)

    def get_connections(self):
        return self.connection_manager.connections
å# port.py
import asyncio
import uuid
import utils
from message import Message
import bcrypt
import secrets
from errors import InvalidDestinationError
from event_queue import EventQueue

class Port:
    def __init__(self, event_queue: EventQueue = None, config=None):
        self.id = str(uuid.uuid4())
        self.address = str(uuid.uuid4())
        self.lock = asyncio.Lock()
        self.event_queue = event_queue if event_queue else EventQueue()
        self.connection_manager = ConnectionManager(self)
        self.message_manager = MessageManager(self)
        self.logger = utils.setup_logger(self)
        self._initialize_handlers()
        if config:
            utils.update_config(self, config)

    def _initialize_handlers(self):
        self._handlers = HandlerFactory.create_handlers(self)

    async def handle(self, event):
        self.logger.debug(f"Handling event: {event}")
        try:
            await self.event_queue.add_event(event)
        except Exception as e:
            self.logger.error(f"Error while handling event: {str(e)}")

    async def connect(self, target):
        async with self.lock:  # Acquire the lock
            await self.connection_manager.connect(target)

    async def disconnect(self, target):
        async with self.lock:  # Acquire the lock
            await self.connection_manager.disconnect(target)

    async def send(self, content, destinations):
        await self.message_manager.send(content, destinations)

    async def receive(self, data):
        await self.message_manager.receive(data)

    async def broadcast(self, content):
        for destination in self.connection_manager.connections:
            await self.message_manager.send(content, destination)

    def get_connections(self):
        return self.connection_manager.connections
