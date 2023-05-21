import os
import logging
import uuid
import sys
from dotenv import load_dotenv
from functools import wraps
import requests

load_dotenv()

API_KEYS = {
    'open_ai': os.getenv('OPEN_AI_API_KEY')
}

def log_func_called(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"{func.__name__} is called.")
        return func(*args, **kwargs)
    return wrapper

def thread_safe_method(method):
    @wraps(method)
    def _method(self, *args, **kwargs):
        with self.lock:
            return method(self, *args, **kwargs)
    return _method

def setup_logger(target, level='INFO'):
    # Create logs directory if not exists
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Create subdirectory for class name if not exists
    if not os.path.exists(f'logs/{target.__class__.__name__}'):
        os.makedirs(f'logs/{target.__class__.__name__}')

    # Create subdirectory for ID if not exists
    if not os.path.exists(f'logs/{target.__class__.__name__}/{target.id}'):
        os.makedirs(f'logs/{target.__class__.__name__}/{target.id}')

    # Use SingletonLogger to get/create a logger
    singleton_logger = SingletonLogger(target.__class__.__name__)
    logger = singleton_logger.get_logger()

    level = level.upper()
    level_dict = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    if level in level_dict:
        logger.setLevel(level_dict[level])
    else:
        logger.setLevel(logging.INFO)  # Default level

    # Add the handlers to the logger
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(f'logs/{target.__class__.__name__}/{target.id}/{target.id}.log')
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger

class SingletonLogger:
    _loggers = {}

    def __new__(cls, classname, *args, **kwargs):
        if classname not in cls._loggers:
            new_logger = super(SingletonLogger, cls).__new__(cls, *args, **kwargs)
            new_logger.logger = logging.getLogger(f"BotLogger-{classname}")
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            new_logger.logger.addHandler(handler)
            cls._loggers[classname] = new_logger
        return cls._loggers[classname]

    def set_level(self, level):
        log_level = getattr(logging, level.upper(), None)
        if not isinstance(log_level, int):
            raise ValueError('Invalid log level: %s' % level)
        self.logger.setLevel(log_level)

    def get_logger(self):
        return self.logger

def generate_unique_id():
    return str(uuid.uuid4())

def run_default_config(target, config):
    for key, value in config.items():
        if callable(value):
            if value.__code__.co_argcount == 1:  # if the function takes one argument
                setattr(target, key, value(target))
            else:  # if the function takes no arguments
                setattr(target, key, value())
        else:
            setattr(target, key, value)

def update_config(target, config):
    # Sets up the target's config - can be used to set up default config or to override it
    restricted_keys = getattr(target, '_restricted_config_keys', set())
    for key, value in config.items():
        if key.startswith('_') or key in restricted_keys:
            target.logger.warning(f"Restricted key {key} in {type(target).__name__} config. Skipping.")
            continue
        setattr(target, key, value() if callable(value) else value)


def verify_config(target, config):
    # Verify that all required keys are present in the config of the target
    for key in config:
        if key not in config:
            target.logger.error(f"Missing required key {key} in {type(target).__name__} config.")
            return False


def generate_name():
    try:
        response = requests.get('https://uinames.com/api/?ext', timeout=5)
        response.raise_for_status()  # this line will raise an HTTPError if the response was unsuccessful
        data = response.json()
        return data['name'] + ' ' + data['surname']

    except requests.exceptions.RequestException as e:
        print(f"Request to uinames API failed: {e}")
        return "Winfo"

    except Exception as e:
        print(f"An error occurred: {e}")
        return "Winfo"