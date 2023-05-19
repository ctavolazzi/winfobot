import uuid
from utils import setup_logger
import threading
import pprint

class Port:
    def __init__(self, config=None):
        self.run_default_config() # Always run this first
        if config and 'owner' in config:
            self._owner = config['owner']  # Set the owner at initialization
            del config['owner']
        if config:
            self.run_config(config) # Run the config if it exists

        self.logger = setup_logger(self, 'DEBUG')
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

    def run_config(self, config):
        for key, value in config.items():
            if key not in self._restricted_config_keys and not key.startswith('_'):  # Skip these attributes
                if callable(value):
                    setattr(self, key, value(self))
                else:
                    setattr(self, key, value)

    def allow_connection(self, hashed_password):
        return hashed_password == self._hashed_password

    def connect(self, connection):
        if self.allow_connection(connection._hashed_password):
            self.connections.add(connection)
            print(f"{connection.__class__.__name__ + ' ' + connection.id} is connected to Port {self.address}")
        else:
            print(f"Connection failed. Incorrect password for Port {self.address}")

    def disconnect(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)
            print(f"{connection.__class__.__name__ + ' ' + connection.id} has been disconnected from Port {self.address}")
        else:
            print(f"{connection.__class__.__name__ + ' ' + connection.id} is not connected to Port {self.address}")

    def add_connection(self, connection):
        if self.allow_connection(connection.hashed_password):
            self.connections.add(connection)
            print(f"{connection.__class__.__name__ + ' ' + connection.id} is connected to Port {self.address}")
        else:
            print(f"Connection failed. Incorrect password for Port {self.address}")

    def remove_connection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)
            print(f"{connection.__class__.__name__ + ' ' + connection.id} has been disconnected from Port {self.address}")
        else:
            print(f"{connection.__class__.__name__ + ' ' + connection.id} is not connected to Port {self.address}")

    def send(self, data, destination):
        # Logic to send data to destination
        pass

    def receive(self, data):
        # Logic to process received data
        pass

    def get_address(self):
        return self.address

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def __repr__(self):
        attributes = vars(self)
        lines = [f'State {self.id}']
        for attr, value in attributes.items():
            if attr in {'id', '_password'}:  # Skip these attributes
                continue
            if attr == 'modules':  # For modules, we want to list the module names only
                value = ', '.join(value.keys())
            elif attr == 'port':  # For port and state, we want to use their IDs
                value = value.id
            elif attr == 'logger':  # For logger, we want to display its level
                value = value.level
            elif attr == 'lock':  # For lock, we want to display its state
                value = 'locked' if value.locked() else 'unlocked'
            lines.append(f'{attr}: {value}')
        return '\n'.join(lines)

    def __str__(self):
        return f"Port {self.address}"
