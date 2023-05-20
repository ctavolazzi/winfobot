import asyncio
from bot import Bot
import openai
from brain import Brain

class Central(Bot):
    def __init__(self, config=None):
        super().__init__(config)
        self.config.update({
            'name': 'Central',
            'type': 'Central',
        })
        self.brain = Brain({'owner': self}) if not hasattr(self, 'brain') else self.brain

    def handle(self, data, source):
        super().handle(data, source)