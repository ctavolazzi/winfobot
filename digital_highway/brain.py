import uuid
import utils

class Brain():
    def __init__(self, config=None):
        self.initialize_default_config()
        self.logger = utils.setup_logger(self, 'DEBUG')

        if config:
            utils.update_config(self, config)

        self.logger.info(f'Initialized {self.__class__.__name__} {self.id} with config {config}')

    def initialize_default_config(self):
        self.id = str(uuid.uuid4())
        self._base_type = self.__class__.__name__
        self._restricted_config_keys = {'id', 'owner', 'logger'}

    def think(self, data):
        # Have the brain think about the data
        return data