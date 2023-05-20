from config import Config

class Brain():
    def __init__(self, config=None):
        if config:
          self.config = Config(config)
        else:
          self.config = Config()
        self.config.update({
          'name': 'Brain',
          'type': 'Brain',
        })

    def think(self, data):
        # Have the brain think about the data
        pass
