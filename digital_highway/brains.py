import uuid
import utils
import threading
from typing import Optional
from utils import thread_safe_method

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

class ThreadedBrain(Brain):
    def __init__(self, owner):
        """Initialize ThreadedBrain with owner

        Args:
            owner (Bot): Owner of this brain instance
        """
        super().__init__(owner)
        self._thread: Optional[threading.Thread] = None

    def start_thinking(self):
        """Start the thinking process"""
        try:
            self._thinking = True
            self._thread = threading.Thread(target=self._think)
            self._thread.start()
        except Exception as e:
            self.bot.logger.error(f"Error starting brain: {str(e)}")

    @thread_safe_method
    def stop_thinking(self):
        """Stop the thinking process"""
        try:
            self._thinking = False
            if self._thread and self._thread.is_alive():
                self._thread.join()
        except Exception as e:
            self.bot.logger.error(f"Error stopping brain: {str(e)}")

    def thinking(self):
        """Brain's thinking logic"""
        while self._thinking:
            # Your thinking logic goes here
            pass
