import uuid
import utils
import threading
from message import Message

class Port:
    def __init__(self, config=None):
        self.run_default_config() # Always run this first
        self.logger = utils.setup_logger(self, 'DEBUG') # Always run this second

        if config and 'owner' in config:
            self._owner = config['owner']  # Set the owner at initialization
            del config['owner']
        if config:
            self.run_config(config) # Run the config if it exists

        self.logger.info(f'Initialized {self.__class__.__name__} {self.id} with config {config}')

        self.lock = threading.Lock()

    def run_default_config(self):
        # Set default values for the port
        self.id = str(uuid.uuid4())
        self.address = str(uuid.uuid4())
        self.connections = set()
        self._owner = None
        self._hashed_password = hash('password')
        self._restricted_config_keys = {'id', 'address', 'connections', 'lock'} # These keys cannot be changed

    def run_config(self, config):
        for key, value in config.items():
            if key not in self._restricted_config_keys and not key.startswith('_'): # Skip these attributes
                if callable(value):
                    setattr(self, key, value(self))
                else:
                    setattr(self, key, value)
            else:
                self.logger.warning(f"Restricted key {key} in Port config. Skipping.")

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        if self._owner is None:
            self._owner = value
        else:
            raise AttributeError("Owner of a port cannot be changed once set.")

    def allow_connection(self, hashed_password):
        return hashed_password == self._hashed_password

    def connect(self, target):
        with self.lock:  # Acquire the lock
            if target in self.connections:
                print(f"{target.__class__.__name__ + ' ' + target.id} is already connected to Port {self.address}")
            elif target is self.owner:
                print(f"Cannot connect {target.__class__.__name__ + ' ' + target.id} to Port {self.address}. It is the owner.")
            elif target is None:
                print(f"Cannot connect {target.__class__.__name__ + ' ' + target.id} to Port {self.address}. It is None.")
            elif target is self:
                print(f"Cannot connect {target.__class__.__name__ + ' ' + target.id} to Port {self.address}. It is itself.")
            elif target is not None and self.allow_connection(target._hashed_password):
                self.connections.add(target)
                print(f"{target.__class__.__name__ + ' ' + target.id} has been connected to Port {self.address}")

    def disconnect(self, target):
        with self.lock:  # Acquire the lock
            if target in self.connections:
                self.connections.remove(target)
                print(f"{target.__class__.__name__ + ' ' + target.id} has been disconnected from Port {self.address}")
            else:
                print(f"{target.__class__.__name__ + ' ' + target.id} is not connected to Port {self.address}")

    def send(self, content, destination):
        message = Message(self, content, destination)
        if destination in self.connections:
            destination.receive(message)

    def receive(self, message):
        # Process the incoming message object and store its content in the bot's memory
        if message is not isinstance(message, Message):
            self.logger.warning(f"Message {message} is not a Message object. It will not be processed.")
            return
        # Optionally, further processing can be applied here

        # Then store in owner's memory
        self.owner.memory.remember(message)

        # And the handle the message
        self.handle(message)

    def handle(self, data):
        """
        This method handles all kinds of data.
        Messages, Configs, Etc. are all handled by this method. This is the brain of the port.
        """
        self.logger.debug(f"Handling data: {data}")
        if 'type' in data.keys():
            print(f"Port {self.address} received data of type {data['type']}")
        else:
            print(f"ERROR: Port {self.address} received data: {data} from {data['sender']} with no type specified.")

    def get_address(self):
        return self.address

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def __repr__(self):
        attributes = vars(self)
        lines = [f'Port {self.id}']
        for attr, value in attributes.items():
            if attr.startswith('_') or attr in {'logger'}:  # Skip these attributes
                continue
            if attr == 'connections':  # Use repr(value) for detailed information
                value = ', '.join([conn.id for conn in value])
            elif attr == 'owner':  # For owner, we want to display the owner's id and type
                value = value.type + value.id
            elif attr == 'lock':
                value = 'locked' if value.locked() else 'unlocked'
            lines.append(f'{attr}: {value}')
        return '\n'.join(lines)

    def __str__(self):
        return f"Port {self.id} \n Address: {self.address} \n Number of Connections: {len(self.connections)} \n Owner: {self.owner}"

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
