import asyncio
from collections import deque
from asyncio import sleep
import logging
from event import Event
import utils

class EventQueue:
    def __init__(self, owner, event_handler):
        self.event_queue = deque()
        self.logger = logging.getLogger('EventQueue')
        self._owner_id = owner.id
        self.is_processing = False
        self.event_handler = event_handler

    async def add_event(self, event):
        self.event_queue.append(event)
        self.logger.info('Event added, current queue length: %s', len(self.event_queue))
        if not self.is_processing:
            self.logger.info('Starting event processing')
            await self.process_events()

    async def process_events(self):
        self.is_processing = True
        while len(self.event_queue) > 0:
            event = self.event_queue.popleft()
            await self.event_handler.handle_event(event)
            await sleep(0.1)  # prevent busy-waiting

            # Once the event is processed, call its callback if it has one
            if event.callback is not None:
                self.logger.info('Calling the event-specific callback function')
                await event.callback()

        self.is_processing = False
        self.logger.info('Event processing finished')