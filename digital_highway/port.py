import utils
import bcrypt
import threading
import uuid
from message import Message
from managers import MessageManager, ConnectionManager
from handlers import Handler, MessageHandler, ConnectionRequestHandler, CommandHandler, EventHandler, MessageEventHandler, CommandEventHandler, GeneralHandler, HandlerFactory
from errors import InvalidDestinationError, UnconnectedDestinationError, UnhandledTypeError, ConnectionError, PortError
from typing import Optional
from utils import thread_safe_method, setup_logger, update_config, hash, verify_hash, get_config

class ConnectionRequest:
    def __init__(self, source_port, token):
        self.source_port = source_port
        self.token = token # The token is now a string

    def __str__(self):
        return f"ConnectionRequest(source_port={self.source_port}, token={self.token})"

class Port:
    _REQUIRED_CONFIG_KEYS = ['id', 'address', 'logger', 'lock', 'handlers']

    _DEFAULT_CONFIG = {
        'id': lambda: str(uuid.uuid4()),
        'address': lambda: str(uuid.uuid4()),
        'lock': lambda: threading.Lock(),
        '_owner': lambda: None,
        '_hashed_password': lambda: hash('password'),
        '_restricted_config_keys': lambda: {'id', 'address', 'lock'},
        '_logger_level': 'DEBUG',
        'is_connected': lambda: False,
        'is_open': lambda: False,
        'is_locked': lambda: False,
        'is_running': lambda: False,
    }

    def __init__(self, config=None):
        self._initialize_default_config()
        self._connection_manager = ConnectionManager(self)
        self._message_manager = MessageManager(self)
        self._initialize_handlers()
        self.setup_logger()

        if config:
            utils.update_config(self, config)

        self.logger.info(f'Initialized {self.__class__.__name__} {self.id} with config {self._DEFAULT_CONFIG}')

    def _initialize_default_config(self):
     utils.run_default_config(self, self._DEFAULT_CONFIG)
     utils.verify_config(self, self._REQUIRED_CONFIG_KEYS)
     # Hash the default password
     self._hashed_password = bcrypt.hashpw('password'.encode(), bcrypt.gensalt())

    def _verify_password(self, password):
        return bcrypt.checkpw(password.encode(), self._hashed_password)

    def _initialize_handlers(self):
        self._handlers = HandlerFactory.create_handlers()

    def setup_logger(self):
        self.logger = utils.setup_logger(self, self._logger_level)
        self.logger.debug(f'Initialized logger for {self.__class__.__name__} {self.id}')

    def _change_password(self, old_password, new_password):
        # Verify the old password
        if bcrypt.checkpw(old_password.encode(), self._hashed_password):
            # Check strength of the new password
            if len(new_password) < 8 or not any(char.isdigit() for char in new_password):
                raise ValueError("New password is not strong enough.")
            if new_password in ["password", "12345678"]:
                raise ValueError("New password is too common.")
            # Once the new password is verified, you can hash it and update the _hashed_password attribute
            salt = bcrypt.gensalt()
            self._hashed_password = bcrypt.hashpw(new_password.encode(), salt)
            self.logger.info("Password changed successfully.")
        else:
            raise ValueError("Old password is incorrect.")

    def handle(self, data):
        if isinstance(data, Message):
            data = data.to_dict()

        self.logger.debug(f"Handling data: {data}")

        if 'type' not in data:
            self.logger.error(f"Port {self.address} received data without 'type': {data}")
            return

        try:
            for handler in self._handlers:
                if handler.can_handle(data['type']):
                    handler.handle(data)
                    break
            else:
                raise UnhandledTypeError(f"Port {self.address} received unknown type: {data['type']}")
        except Exception as e:
            self.logger.error(f"Error while handling data: {str(e)}")

    def connect(self, target):
        with self.lock:  # Acquire the lock
            self._connection_manager.connect(target)

    def disconnect(self, target):
        with self.lock:  # Acquire the lock
            self._connection_manager.disconnect(target)

    def handle_connection_request(self, request):
        if not isinstance(request, ConnectionRequest):
            return False
        # The hashed token should be stored somewhere safe when the connection request was created
        # Here we assume that it's stored in self._hashed_token
        if bcrypt.checkpw(request.token.encode(), self._hashed_token):
            return True
        return False

    def send(self, content, destinations):
        self._message_manager.send(content, destinations)

    def receive(self, data):
        self._message_manager.receive(data)

    def broadcast(self, content):
        for destination in self._connection_manager.connections:
            self._message_manager.send(content, destination)

    def get_connections(self):
        return self._connection_manager.connections

    def lock(self):
        self.is_locked = True

    def unlock(self):
        self.is_locked = False

def connect_ports(port1, port2):
    port1.connect(port2)
    port2.connect(port1)

def disconnect_ports(port1, port2):
    port1.disconnect(port2)
    port2.disconnect(port1)

def main():
    # Create two ports
    p1 = Port()
    p2 = Port()
    p3 = Port()

    # Connect the ports
    connect_ports(p1, p2)
    connect_ports(p1, p3)

    # Send data from p1 to p2
    p1.send("Hello World!", p2)

    # Send data from p1 to all connected ports
    p1.broadcast("Broadcast message")

    # Disconnect the ports
    disconnect_ports(p1, p2)
    disconnect_ports(p1, p3)

    # Make sure the ports disconnected
    try:
        p1.send("Hello World!", p2)
    except InvalidDestinationError:
        print("All tests pass.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    else:
        print("Test failed: message sent to port that should be disconnected.")

if __name__ == '__main__':
    main()
