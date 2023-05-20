import datetime
import utils

class Config:
    DEFAULT_CONFIG_SELF = {}

    DEFAULT_CONFIG = {
        'settings': lambda: {},
        'timestamp': lambda: datetime.datetime.now()
    }

    def __init__(self, config=None):
        self.run_default_config() # Always run this first
        self.logger = utils.setup_logger(self, 'DEBUG') # Always run this second

        if config:
            self.run_config(config) # Run the config if it exists

    def run_default_config(self):
        for key, default_value_func in self.DEFAULT_CONFIG_SELF.items():
            setattr(self, key, default_value_func(self))
        for key, default_value_func in self.DEFAULT_CONFIG.items():
            setattr(self, key, default_value_func())

    def run_config(self, config):
        for key, value in config.items():
            if hasattr(self, key) and not key.startswith('_'): # Skip these attributes
                setattr(self, key, value)
        self.logger.info(f"Updated config for {self.__class__.__name__} with {config}")

    # ... rest of your code ...

    def update(self, updates):
        if not isinstance(updates, dict):
            raise TypeError('updates should be a dictionary')
        self.settings.update(updates)
        self.timestamp = datetime.datetime.now()


    def __getitem__(self, key):
        try:
            return self.settings[key]
        except KeyError:
            raise KeyError(f'The key "{key}" does not exist in the configuration settings.')

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def __contains__(self, key):
        return key in self.settings

    def __repr__(self):
        safe_settings = {k: '***' if k.lower().endswith('password') else v for k, v in self.settings.items()}
        return f'Config({safe_settings})'

    def __str__(self):
        safe_settings = {k: '***' if k.lower().endswith('password') else v for k, v in self.settings.items()}
        return f'Config({safe_settings})'
