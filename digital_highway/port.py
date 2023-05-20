import uuid
import utils
import threading
from message import Message

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
        command = data['content']['command']
        if command == 'someCommand':
            pass  # Do something...


class DataHandler(Handler):
    @staticmethod
    def can_handle(type):
        return type == 'Data'

    def handle(self, data):
        payload = data['content']
        # Do something with payload...


class Port:
    _REQUIRED_CONFIG_KEYS = ['id', 'address', 'logger', 'lock', 'handlers']

    _DEFAULT_CONFIG = {
        'id': lambda: str(uuid.uuid4()),
        'address': lambda: str(uuid.uuid4()),
        'connections': lambda: set(),
        '_owner': lambda: None,
        '_manager': lambda: None,
        '_hashed_password': lambda: hash('password'),
        '_restricted_config_keys': lambda: {'id', 'address', 'connections', 'lock'},
        'logger': lambda: utils.setup_logger('Port', 'DEBUG'),
        'lock': lambda: threading.Lock(),
        'handlers': lambda: [
            CommandHandler(),
            DataHandler(),
            # add more handlers here as you define them
            ],
        'is_connected': lambda: False,
        'is_open': lambda: False,
        'is_locked': lambda: False,
        'is_running': lambda: False,
    }

    def __init__(self, config=None):
        self.initialize()
        # ... rest of your existing code

    def initialize(self):
        # Set up the port's default config
        utils.run_config(self, self._DEFAULT_CONFIG)
        utils.verify_config(self, self._DEFAULT_CONFIG)
        self.logger.info(f'Initialized {self.__class__.__name__} {self.id} with config {self._DEFAULT_CONFIG}')

    def handle(self, data):
        if isinstance(data, Message):
            data = data.to_dict()

        self.logger.debug(f"Handling data: {data}")

        if 'type' not in data:
            self.logger.error(f"Port {self.address} received data without 'type': {data}")
            return

        for handler in self.handlers:
            if handler.can_handle(data['type']):
                handler.handle(data)
                break
        else:
            self.logger.error(f"Port {self.address} received unknown type: {data['type']}")

    def connect(self, target):
        with self.lock:  # Acquire the lock
            if target in self.connections:
                self.logger.error(f"{target.__class__.__name__ + ' ' + target.id} is already connected to Port {self.address}")
            elif target is self.owner:
                self.logger.error(f"Cannot connect {target.__class__.__name__ + ' ' + target.id} to Port {self.address}. It is the owner.")
            elif target is None:
                self.logger.error(f"Cannot connect None to Port {self.address}.")
            elif target is self:
                self.logger.error(f"Cannot connect Port {self.address} to itself.")
            elif target.verify_password(self._hashed_password):
                self.connections.add(target)
                self.logger.info(f"{target.__class__.__name__ + ' ' + target.id} has been connected to Port {self.address}")

    def disconnect(self, target):
        with self.lock:  # Acquire the lock
            if target in self.connections:
                self.connections.remove(target)
                self.logger.info(f"{target.__class__.__name__ + ' ' + target.id} has been disconnected from Port {self.address}")
            else:
                self.logger.error(f"{target.__class__.__name__ + ' ' + target.id} is not connected to Port {self.address}")

    def send(self, content, destination):
        if destination in self.connections:
            message = self.create_message(content, destination)
            self.owner.memory.remember(message)
            destination.receive(message)
        else:
            self.logger.error(f"Cannot send message to unconnected destination {destination.__class__.__name__ + ' ' + destination.id}")

    def create_message(self, content, destination):
        return Message(self, content, destination)

    # rest of your existing code

def main():
    # Create two ports
    p1 = Port()
    p2 = Port()

    # Connect the ports
    p1.connect(p2)
    p2.connect(p1)

    # Send data from p1 to p2
    p1.send("Hello World!", p2)

    # Disconnect the ports
    p1.disconnect(p2)
    p2.disconnect(p1)

    # Try to send data again
    p1.send("Hello World!", p2)

if __name__ == '__main__':
    main()
