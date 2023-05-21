import uuid
import utils
import threading
from message import Message
import bcrypt

class UnconnectedDestinationError(Exception):
    pass

class UnhandledTypeError(Exception):
    pass

class InvalidDestinationError(Exception):
    pass

class Handler:
    @staticmethod
    def can_handle(type):
        raise NotImplementedError("This method should be overridden in subclass")

    def handle(self, data):
        raise NotImplementedError("This method should be overridden in subclass")

class CommandHandler(Handler):
    @staticmethod
    def can_handle(type):
        return type == 'Command'

    def handle(self, data):
        command = data['content']
        # Handle the data...
        return command

class DataHandler(Handler):
    @staticmethod
    def can_handle(type):
        return type == 'Data'

    def handle(self, data):
        payload = data['content']
        # Handle the data...
        return payload

class HandlerFactory:
    _handlers = []

    @classmethod
    def register_handler(cls, handler):
        cls._handlers.append(handler)

    @staticmethod
    def create_handlers():
        return [handler() for handler in HandlerFactory._handlers]

# Register handlers
HandlerFactory.register_handler(CommandHandler)
HandlerFactory.register_handler(DataHandler)

class ConnectionError(Exception):
    pass

class ConnectionManager:
    def __init__(self, port):
        self.port = port
        self.connections = set()

    def connect(self, target):
        if target in self.connections:
            raise ConnectionError(f"{target.__class__.__name__ + ' ' + target.id} is already connected to Port {self.port.address}")
        elif target is self.port._owner:
            raise ConnectionError(f"Cannot connect {target.__class__.__name__ + ' ' + target.id} to Port {self.port.address}. It is the owner.")
        elif target is None:
            raise ConnectionError(f"Cannot connect None to Port {self.port.address}.")
        elif target is self.port:
            raise ConnectionError(f"Cannot connect Port {self.port.address} to itself.")
        # Else if it passes the verification it will be added to the connections list
        elif hasattr(target, '_verify_password') and target._verify_password(self.port._hashed_password):
            self.connections.add(target)
            self.port.logger.info(f"{target.__class__.__name__ + ' ' + target.id} has been connected to Port {self.port.address}")
        else:
            raise ConnectionError(f"Could not connect {target.__class__.__name__ + ' ' + target.id} to Port {self.port.address}.")
        return self

    def disconnect(self, target):
        if target in self.connections:
            self.connections.remove(target)
            self.port.logger.info(f"{target.__class__.__name__ + ' ' + target.id} has been disconnected from Port {self.port.address}")
        else:
            raise ConnectionError(f"{target.__class__.__name__ + ' ' + target.id} is not connected to Port {self.port.address}")
        return self

class MessageManager:
    _REQUIRED_CONFIG_KEYS = ['id', 'logger', 'lock', 'port']

    _DEFAULT_CONFIG = {
        'id': lambda: str(uuid.uuid4()),
        'lock': lambda: threading.Lock(),
        '_port': None,
        '_messages': lambda: set(),
        '_logger_level': 'DEBUG'
    }

    def __init__(self, port):
        utils.run_default_config(self, self._DEFAULT_CONFIG)
        utils.verify_config(self, self._REQUIRED_CONFIG_KEYS)
        self._port = port
        self.logger = utils.setup_logger(self)
        self.logger.info(f'Initialized {self.__class__.__name__} {self.id} for Port {self._port.id}')

    def send(self, content: str, destinations):
        self.logger.debug(f'Current connections: {self._port.get_connections()}')
        current_connections = self._port.get_connections()
        if not isinstance(destinations, list):
            destinations = [destinations]
        with self.lock:  # Acquire the lock
            for destination in destinations:
                if destination in current_connections:
                    message = Message(self, content, destination)
                    self._messages.add(message)
                    destination.receive(message)
                    self.logger.info(f'Message sent from Port {self._port.id} to {destination.__class__.__name__ + " " + destination.id}.')
                else:
                    self.logger.error(f"Cannot send message to unconnected destination {destination.__class__.__name__ + ' ' + destination.id}.")
                    raise InvalidDestinationError(f"Cannot send message to unconnected destination {destination.__class__.__name__ + ' ' + destination.id}.")

    def receive(self, message: Message):
        if not isinstance(message, Message):
            raise TypeError("The 'message' parameter should be an instance of the 'Message' class.")
        with self.lock:  # Acquire the lock
            self._messages.add(message)
            self.logger.info(f'Message received at Port {self._port.id}.')

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

    def _initialize_handlers(self):
        self._handlers = HandlerFactory.create_handlers()

    def setup_logger(self):
        self.logger = utils.setup_logger(self, self._logger_level)
        self.logger.debug(f'Initialized logger for {self.__class__.__name__} {self.id}')

    def _verify_password(self, password_hash):
        return self._hashed_password == password_hash

    def _change_password(self, old_password, new_password):
        # Verify the old password:
        if bcrypt.checkpw(old_password.encode(), self._hashed_password):
            # Check strength of the new password (this is a simplified check):
            if len(new_password) < 8 or not any(char.isdigit() for char in new_password):
                raise ValueError("New password is not strong enough.")
            # Reject common passwords (here you would check against a full list):
            if new_password in ["password", "12345678"]:
                raise ValueError("New password is too common.")
            # Once the new password is verified, you can hash it and update the _hashed_password attribute.
            # Here we're using bcrypt for hashing, and a salt for additional security.
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