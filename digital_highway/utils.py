import os
import logging

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
