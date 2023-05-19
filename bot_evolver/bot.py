import threading
import uuid
from memory import Memory
from ability import Ability
import logging
import datetime
import openai

class Bot:
    """
    The Bot class represents an evolving bot with the ability to gain new abilities.

    Attributes:
    id (str): a unique identifier for the bot.
    abilities (dict of Ability): the abilities the bot currently has.
    """
    def __init__(self, id=None, setup_config_func=None):
        """
        The constructor for the Bot class.

        Parameters:
        id (str): a unique identifier for the bot.
        setup_config_func (function): a function to set up the bot's initial abilities.
        """
        self.id = id if id else str(uuid.uuid4())
        self.lock = threading.Lock()
        self.setup_logger()
        self.stats = {}
        self.abilities = {}
        self.info = {}
        self.inventory = {}
        self.memory = Memory()
        self.conversations = []
        self.logger.info(f'Bot {self.id} created.')

        if setup_config_func:
            try:
                setup_config_func(self)
            except Exception as e:
                self.logger.error(f'An error occurred while setting up bot {self.id}: {e}')
                raise e

    def __str__(self):
        return f'Bot {self.id}'

    def __repr__(self):
        return f'Bot {self.id}'

    def setup_logger(self):
        self.logger = logging.getLogger(self.id)
        handler = logging.FileHandler(self.id + '.log')
        formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def remember_and_log(self, memory):
        self.remember(memory)
        self.logger.info(f'Bot {self.id} remembered {memory}')

    def remember(self, memory):
        self.memory.add_memory(memory)

    def add_ability(self, name, action):
        if name in self.abilities:
            raise ValueError(f'Ability {name} already exists on bot {self.id}. Use a different name.')
        if not callable(action):
            raise TypeError(f'Action for ability {name} must be a function. Got {type(action).__name__} instead.')

        self.abilities[name] = Ability(name, action)

    def configure_ability(self, name, *args, **kwargs):
        if name not in self.abilities:
            raise ValueError(f'Ability {name} does not exist on bot {self.id}.')

        try:
            self.abilities[name].perform(self, *args, **kwargs)
            self.remember_and_log(f'Configured ability {name} with args {args} and kwargs {kwargs}')
        except Exception as e:
            self.logger.error(f'An error occurred while configuring ability {name} on bot {self.id}: {e}')
            raise e

    # Chat
    def generate_message(self, conversation):
        message = conversation.generate_response(self.id)
        return message

    def join_conversation(self, conversation):
        self.conversations.append(conversation)
        conversation.add_bot(self)

    def leave_conversation(self, conversation):
        self.conversations.remove(conversation)
        conversation.remove_bot(self)

    def speak(self, message):
        for conversation in self.conversations:
            formatted_message = {'role': 'assistant', 'content': message, 'source': self.id}
            conversation.broadcast_message(formatted_message)


    # Event handlers
    def trigger_event(self, event):
      if event['type'] == 'message':
        self.handle_message_event(event)

    def handle_message_event(self, event):
        message = event['message']
        conversation = event['conversation']
        self.remember_and_log(f'Heard message {message} in conversation {conversation.id}')
        self.handle_message(message, conversation)

    def handle_message(self, message, conversation):
        self.speak(self.generate_message(conversation))

    # Getters
    def get_memories(self):
        return self.memory.get_memories()

    def get_stats(self):
        return self.stats

    def get_abilities(self):
        return self.abilities

    def get_info(self):
        return self.info

    def get_inventory(self):
        return self.inventory

    def get_memory(self):
        return self.memory

    def get_id(self):
        return self.id

    # Setters
    def set_info(self, info):
        self.info = info

    def set_stats(self, stats):
        self.stats = stats

    def set_abilities(self, abilities):
        self.abilities = abilities

    # Tests
    def test_self(self):
        assert hasattr(self, 'add_ability'), "add_ability method is missing"
        assert hasattr(self, 'configure_ability'), "configure_ability method is missing"
        print("All tests pass.")
