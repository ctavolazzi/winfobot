# event_queue.py
from typing import List, Dict, Type, Any, Callable, Union
from threading import Lock
from collections import defaultdict
from utils import setup_logger, generate_unique_id
from events import Event
from handlers import EventHandler
import asyncio

class EventQueue:
    def __init__(self):
        self.id = generate_unique_id()
        self.lock = Lock()
        self.event_queue = asyncio.Queue()
        self.event_handlers: Dict[Type[Event], List[Union[EventHandler, Callable[[Event], Any]]]] = defaultdict(list)
        self.logger = setup_logger(self)
        self.processing_task = None

    def register_handler(self, event_type: Type[Event], handler: EventHandler):
        with self.lock:
            if isinstance(handler, EventHandler):
                self.event_handlers[event_type].append(handler)
            else:
                raise ValueError("Handler must be an instance of EventHandler")

    async def add_event(self, event: Event):
        await self.event_queue.put(event)
        self.logger.info(f'Event {event.id} added to the queue. Current queue length: {self.event_queue.qsize()}')
        if self.processing_task is None or self.processing_task.done():
            self.processing_task = asyncio.create_task(self.process_events())

    async def shutdown(self):
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        self.logger.info('Event processing loop has been stopped.')

    async def process_single_event(self, event, handler):
        try:
            await handler.handle(event)
            self.logger.info(f"Event {event.id} processed successfully by handler {type(handler).__name__}")
        except Exception as e:
            self.logger.error(f"Error processing event {event.id} with handler {type(handler).__name__}: {str(e)}", exc_info=True)

    async def process_events(self):
        while not self.event_queue.empty():
            event = await self.event_queue.get()
            handlers = self.event_handlers.get(type(event), [])
            if not handlers:
                self.logger.warning(f"No handler registered for event {type(event).__name__}, ID: {event.id}")
                self.event_queue.task_done()
                continue
            handler_coroutines = [self.process_single_event(event, handler) for handler in handlers]
            try:
                await asyncio.gather(*handler_coroutines)
                self.event_queue.task_done()
            except Exception as e:
                self.logger.error(f"Error processing event {event.id}: {str(e)}", exc_info=True)
                self.event_queue.task_done()
                continue
        self.logger.info('Event processing loop has been stopped.')

    def __repr__(self):
        return f"EventQueue(id={self.id}, queue_size={self.event_queue.qsize()})"

    def __str__(self):
        return self.__repr__()

