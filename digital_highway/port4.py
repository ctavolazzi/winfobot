import uuid
import utils
import threading
from message import Message
import bcrypt
import secrets

class ConnectionRequest:
    def __init__(self, source_port, token):
        self.source_port = source_port
        self.token = token

class UnconnectedDestinationError(Exception):
    pass

class UnhandledTypeError(Exception):
    pass

class InvalidDestinationError(Exception):
    pass

class ConnectionError(Exception):
    pass

class ConnectionManager:
    ...
    # The same code

class MessageManager:
    ...
    # The same code

class Port:
    _REQUIRED_CONFIG_KEYS = ['id', 'address', 'logger', 'lock', 'handlers']

    _DEFAULT_CONFIG = {
        'id': lambda: str(uuid.uuid4()),
        'address': lambda: str(uuid.uuid4()),
        '_thread_lock': lambda: threading.Lock(),  # Rename the lock to _thread_lock
        '_owner': lambda: None,
        '_hashed_password': lambda: hash('password'),
        '_hashed_token': lambda: None,  # Adding a hashed_token attribute
        '_restricted_config_keys': lambda: {'id', 'address', '_thread_lock'},
        '_logger_level': 'DEBUG',
        'is_connected': lambda: False,
        'is_open': lambda: False,
        'is_locked': lambda: False,
        'is_running': lambda: False,
    }

    ...
    # The same code

    def connect(self, target):
        with self._thread_lock:  # Acquire the lock
            # Generate a token and hash it
            token = secrets.token_hex(16)
            self._hashed_token = bcrypt.hashpw(token.encode(), bcrypt.gensalt())
            self._connection_manager.connect(target)

    ...
    # The same code

    def lock(self):
        with self._thread_lock:  # Acquire the lock
            self.is_locked = True

    def unlock(self):
        with self._thread_lock:  # Acquire the lock
            self.is_locked = False

    # Class methods to replace the connect_ports and disconnect_ports functions
    @classmethod
    def connect_ports(cls, port1, port2):
        port1.connect(port2)
        port2.connect(port1)

    @classmethod
    def disconnect_ports(cls, port1, port2):
        port1.disconnect(port2)
        port2.disconnect(port1)

def main
