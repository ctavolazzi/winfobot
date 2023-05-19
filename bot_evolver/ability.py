import datetime
from utils import setup_logger

class Ability:
    def __init__(self, name, action, requirements=None):
        self.name = name
        self.action = action
        self.usage_logs = []
        if requirements:
            self.requirements = requirements
        self.logger = setup_logger(name + '_logger', name + '.log')

    def perform(self, bot, *args, **kwargs):
        try:
            self.action(bot, *args, **kwargs)
        except Exception as e:
            self.logger.error(f'An error occurred while performing ability {self.name}: {e}')
            raise e

    # Log the usage of the ability
    def log_usage(self, bot, *args, **kwargs):
        self.usage_logs.append({
            'bot_id': bot.id,
            'args': args,
            'kwargs': kwargs,
            'timestamp': datetime.datetime.now()
        })
        self.logger.info(f'Bot {bot.id} used ability {self.name} with args {args} and kwargs {kwargs} at {datetime.datetime.now()}')

    # Get the usage logs for the ability
    def get_usage_logs(self):
        return self.usage_logs

    # Test the ability
    def test_self(self):
        assert hasattr(self, 'name'), "name attribute is missing"
        assert hasattr(self, 'action'), "action attribute is missing"
        assert hasattr(self, 'usage_logs'), "usage_logs attribute is missing"
        assert hasattr(self, 'perform'), "perform method is missing"
        assert hasattr(self, 'log_usage'), "log_usage method is missing"
        assert hasattr(self, 'get_usage_logs'), "get_usage_logs method is missing"
        print("All tests pass.")