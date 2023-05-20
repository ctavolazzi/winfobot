from config import Config

class Brain():
    def __init__(self, config=None):
        self.config = Config(config if config else {})  # Use an empty dictionary if no configuration is provided
        self.config.update({
          'name': 'Brain',
          'type': 'Brain',
        })

    def think(self, data):
        # Have the brain think about the data
        return data
