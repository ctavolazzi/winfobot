from abc import ABC

class Event(ABC):
    pass

class MessageEvent(Event):
    def __init__(self, message, source):
        self.message = message
        self.source = source

class CommandEvent(Event):
    def __init__(self, command, *args):
        self.command = command
        self.args = args
