from datetime import datetime
from abc import ABC
from typing import Dict, Any
from utils import generate_unique_id


class EventLog:
    def __init__(self):
        self.history = []

    def add_entry(self, entry):
        self.history.append((datetime.now(), entry))

    def __str__(self):
        return str(self.history)

    def __repr__(self):
        return str(self.history)

    def __iter__(self):
        return iter(self.history)

    def __getitem__(self, index):
        return self.history[index]

    def __len__(self):
        return len(self.history)

    def __contains__(self, item):
        return item in self.history

    def __reversed__(self):
        return reversed(self.history)

    def __add__(self, other):
        return self.history + other

    def __radd__(self, other):
        return other + self.history

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


class Event(ABC):
    def __init__(self, payload: str):
        self._id = generate_unique_id()
        self._payload = payload
        self._timestamp = datetime.now()
        self._metadata: Dict[str, Any] = {}

    @property
    def id(self) -> str:
        return self._id

    @property
    def payload(self) -> str:
        return self._payload

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata

    def add_metadata(self, key: str, value: Any) -> None:
        self._metadata[key] = value

class MessageEvent(Event):
    def __init__(self, message: str, sender: str):
        super().__init__(message)
        self._sender = sender

    @property
    def sender(self) -> str:
        return self._sender

class CommandEvent(Event):
    def __init__(self, command: str, target: str, params: Dict[str, Any] = None):
        super().__init__(command)
        self._target = target
        self._params = params if params else {}

    @property
    def target(self) -> str:
        return self._target

    @property
    def params(self) -> Dict[str, Any]:
        return self._params

class TestEvent(Event):
    def __init__(self, source, test_data, target):
        super().__init__(test_data)
        self._source = source
        self._target = target

    @property
    def source(self):
        return self._source

    @property
    def target(self):
        return self._target

    @property
    def payload(self):
        return self._payload