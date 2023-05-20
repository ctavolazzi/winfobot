import datetime

class Config:
    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        elif not isinstance(settings, dict):
            raise TypeError('settings should be a dictionary')
        self.settings = settings
        self.timestamp = datetime.datetime.now()

    # ...

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
