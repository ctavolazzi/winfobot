# event_queue.py
from typing import List, Dict, Type, Any, Callable, Union
from threading import Lock
from collections import defaultdict
from utils import setup_logger, thread_safe_method
from events import Event
from event_handlers import EventHandler
from errors import RetryExceededError, HandleError
import asyncio

class RetryExceededError(Exception):
    pass

class EventQueue:
    def __init__(self):
        self.lock = Lock()
        self.event_queue = asyncio.PriorityQueue()
        self.event_handlers: Dict[Type[Event], List[Union[EventHandler, Callable[[Event], Any]]]] = defaultdict(list)
        self.logger = setup_logger(self)
        self.processing_task = None
        self.retry_counts: Dict[str, int] = defaultdict(int)  # Add a dictionary to track the retry counts for each event
        self.max_retries = 3  # Set the maximum number of retries to 3
        self.retry_delay = 5  # Set the delay between retries to 5 seconds
        self.retry_queue = asyncio.Queue()  # Create a queue to hold the events that need to be retried
        self.retry_task = None  # Create a task to process the retry queue
        self.retry_processing = False  # Add a flag to indicate if the retry queue is being processed

    def register_handler(self, event_type: Type[Event], handler: EventHandler):
        with self.lock:
            if isinstance(handler, EventHandler):
                self.event_handlers[event_type].append(handler)
            else:
                raise ValueError("Handler must be an instance of EventHandler")

    @thread_safe_method
    async def add_event(self, event: Event, priority: int = 0):
        await self.event_queue.put((-priority, event))
        self.retry_counts[event.id] = self.max_retries  # Initialize the retry count
        self.logger.info(f'Event {event.id} added to the queue. Current queue length: {self.event_queue.qsize()}')
        if self.processing_task is None or self.processing_task.done():
            self.processing_task = asyncio.create_task(self.process_events())

    async def shutdown(self):  # New method to stop the processing loop
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        self.logger.info('Event processing loop has been stopped.')

    async def process_single_event(self, event, handler, priority):
        """Process a single event with the provided handler."""
        try:
            await asyncio.wait_for(handler.handle(event), timeout=self.handler_timeout)  # Set a timeout
            self.logger.info(f"Event {event.id} processed successfully by handler {type(handler).__name__} with ID {handler.id}")
            self.retry_counts[event.id] = 0
        except TimeoutError:
            self.logger.error(f"Timeout processing event {event.id} with handler {type(handler).__name__}, ID {handler.id}. Retrying...")
            self.retry_counts[event.id] -= 1
            retry_delay = self.calculate_retry_delay(self.retry_counts[event.id])
            await asyncio.sleep(retry_delay)  # wait for a calculated delay before retrying
        except HandlerError as e:  # Specific exception for handler error
            self.retry_counts[event.id] -= 1
            if self.retry_counts[event.id] > 0:
                await asyncio.sleep(self.retry_delay)
                await self.event_queue.put((priority, event))
                self.logger.error(f"HandlerError processing event {event.id} with handler {type(handler).__name__}, ID {handler.id}: {str(e)}. Retrying (remaining attempts {self.retry_counts[event.id]})...", exc_info=True)
            else:
                raise RetryExceededError(f"Error processing event {event.id} with handler {type(handler).__name__}, ID {handler.id}: {str(e)}") from e

    @classmethod
    def register_handler(cls, event_type: Type[Event]):
        def decorator(handler_class: Type[EventHandler]):
            if not issubclass(handler_class, EventHandler):
                raise TypeError("Handler must be a subclass of EventHandler")
            cls._handlers[event_type] = handler_class()
            return handler_class
        return decorator

    def calculate_retry_delay(self, retry_count: int) -> float:
        return min(self.max_retry_delay, self.base_retry_delay * 2 ** retry_count)

    @log_func_called
    async def process_events(self):
        while not self.event_queue.empty():
            _, event = await self.event_queue.get()
            handlers = self._handlers.get(type(event), [])
            if not handlers:
                self.logger.warning(f"No handler registered for event {type(event).__name__}, ID: {event.id}")
                self.event_queue.task_done()
                continue
            handler_coroutines = [handler.handle(event) for handler in handlers]
            try:
                await asyncio.gather(*handler_coroutines)
                self.logger.info(f"Event {event.id} processed successfully")
                self.retry_counts[event.id] = 0
            except Exception as e:
                self.retry_counts[event.id] -= 1
                if self.retry_counts[event.id] > 0:
                    retry_delay = self.calculate_retry_delay(self.retry_counts[event.id])
                    await asyncio.sleep(retry_delay)
                    await self.event_queue.put((priority, event))
                    self.logger.error(f"Error processing event {event.id}, retrying after {retry_delay} seconds: {str(e)}", exc_info=True)
                else:
                    self.logger.error(f"Error processing event {event.id}, max retry attempts exceeded: {str(e)}", exc_info=True)
            finally:
                self.event_queue.task_done()