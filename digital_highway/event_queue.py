from collections import deque
from asyncio import sleep
import logging

class EventQueue:
    def __init__(self):
        self.event_queue = deque()
        self.logger = logging.getLogger('EventQueue')

    async def add_event(self, event):
        self.event_queue.append(event)

    async def process_events(self, event_handler):
        while True:
            if self.event_queue:
                event = self.event_queue.popleft()
                await event_handler.handle_event(event)
            await sleep(0.1)  # prevent busy-waiting
