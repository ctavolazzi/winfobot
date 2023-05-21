import asyncio

class Event:
    def __init__(self, data, callback=None):
        self.data = data
        if callback is not None and not asyncio.iscoroutinefunction(callback):
            callback = asyncio.coroutine(callback)
        self.callback = callback
