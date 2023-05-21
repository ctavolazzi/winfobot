from typing import List, Dict, Type, Any, Callable, Union
import logging
import asyncio
from abc import ABC, abstractmethod
from threading import Lock
from collections import defaultdict

from utils import generate_unique_id, setup_logger, log_func_called, thread_safe_method

class Event(ABC):
    def __init__(self, message: str):
        self.id = generate_unique_id()
        self.message = message

class EventHandler(ABC):
    def __init__(self):
        self.id = generate_unique_id()
        self.logger = setup_logger(self)

    @abstractmethod
    async def handle(self, event: Event):
        pass

class MessageEvent(Event):
    def __init__(self, message: str):
        super().__init__(message)

class CommandEvent(Event):
    def __init__(self, command: str):
        super().__init__(command)

class MessageEventHandler(EventHandler):
    @log_func_called
    async def handle(self, event: MessageEvent):
        self.logger.info(f"Message Event Received. Content: {event.message}")

class CommandEventHandler(EventHandler):
    @log_func_called
    async def handle(self, event: CommandEvent):
        self.logger.info(f"Command Event Received. Command: {event.message}")

class EventQueue:
    def __init__(self):
        self.lock = Lock()
        self.event_queue = asyncio.PriorityQueue()
        self.event_handlers: Dict[Type[Event], List[Union[EventHandler, Callable[[Event], Any]]]] = defaultdict(list)
        self.logger = setup_logger(self)
        self.processing_task = None  # Track the processing task

    @thread_safe_method
    def register_handler(self, event_type: Type[Event], handler: Union[EventHandler, Callable[[Event], Any]]):
        if callable(handler) or isinstance(handler, EventHandler):
            self.event_handlers[event_type].append(handler)
        else:
            raise ValueError("Handler must be an instance of EventHandler or a callable")

    @thread_safe_method
    async def add_event(self, event: Event, priority: int = 0):
        await self.event_queue.put((-priority, event))  # Reverse the priority so high priority is dequeued first
        self.logger.info(f'Event {event.id} added to the queue. Current queue length: {self.event_queue.qsize()}')
        # Start a new processing task if necessary
        if self.processing_task is None or self.processing_task.done():
            self.processing_task = asyncio.create_task(self.process_events())

    @log_func_called
    async def process_events(self):
        while not self.event_queue.empty():
            priority, event = await self.event_queue.get()
            handlers = self.event_handlers.get(type(event), [])
            if not handlers:
                self.logger.warning(f"No handler registered for event {type(event).__name__}, ID: {event.id}")
                self.event_queue.task_done()
                continue
            for handler in handlers:
                try:
                    if isinstance(handler, EventHandler):
                        await handler.handle(event)
                    elif callable(handler):
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)
                    self.logger.info(f"Event {event.id} processed successfully by handler {type(handler).__name__} with ID {handler.id}")
                except Exception as e:
                    self.logger.error(f"Error processing event {event.id} with handler {type(handler).__name__}, ID {handler.id}: {str(e)}", exc_info=True)
                    # Put the event back in the queue with the same priority
                    await asyncio.sleep(1)  # wait for 1 second before retrying
                    await self.event_queue.put((priority, event))
                    break  # stop processing this event with other handlers
                finally:
                    self.event_queue.task_done()