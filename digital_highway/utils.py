import os
import logging
import uuid

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

    # Create a custom logger
    logger = logging.getLogger(target.id)
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

def generate_unique_id():
    return str(uuid.uuid4())

def run_config(target, config):
    # Sets up the target's config - can be used to set up default config or to override it
    for key, value in config.items():
        if key not in target._restricted_config_keys and not key.startswith('_'): # Skip these attributes
            if callable(value):
                setattr(target, key, value(target))
            else:
                setattr(target, key, value)
        else:
            target.logger.warning(f"Restricted key {key} in {type(target).__name__} config. Skipping.")

def verify_config(target, config):
    # Verify that all required keys are present in the config of the target
    for key in target._required_config_keys:
        if key not in config:
            target.logger.error(f"Missing required key {key} in {type(target).__name__} config.")
            return False