# Description: Conversation class for storing conversation history and generating responses
from utils import setup_logger
import uuid
import openai
import logging

class Conversation:
    def __init__(self, api_key, model="gpt-3.5-turbo", max_exchange=None, id=None):
        if id:
            self.id = id
        else:
            self.id = str(uuid.uuid4())
        self.api_key = api_key
        self.model = model
        self.messages = []
        self.bots = []
        self.setup_logger()
        if max_exchange:
            self.max_exchange = max_exchange
        else:
            self.max_exchange = float('inf')

    def setup_logger(self):
        self.logger = logging.getLogger(self.id)
        handler = logging.FileHandler(self.id + '.log')
        formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def add_bot(self, bot):
        self.bots.append(bot)
        bot.conversations.append(self)
        self.logger.info(f"Bot {bot.id} added to the conversation")

    def remove_bot(self, bot):
        self.bots.remove(bot)
        bot.conversations.remove(self)
        self.logger.info(f"Bot {bot.id} removed from the conversation")

    def add_and_broadcast_message(self, message):
        if len(self.messages) >= self.max_exchange:
            self.logger.warning('Maximum conversation exchange limit reached. Resetting conversation.')
            self.reset_conversation()
        self.messages.append(message)
        for bot in self.bots:
            if bot.id != message['role']:  # Ensures that the bot that sent the message does not receive it
                bot.trigger_event({'type': 'message', 'message': message, 'conversation': self})

    def add_message(self, message):
        if len(self.messages) >= self.max_exchange:
            self.logger.warning('Maximum conversation exchange limit reached. Resetting conversation.')
            self.reset_conversation()
        self.messages.append(message)

    def get_conversation_history(self):
        return self.messages

    def broadcast_message(self, message):
        for bot in self.bots:
            if bot.id != message['role']:  # Ensures that the bot that sent the message does not receive it
                bot.remember_and_log(message)

    def reset_conversation(self):
        self.messages = []

    def generate_response(self, bot_id):
        openai.api_key = self.api_key
        model = "gpt-3.5-turbo"  # or any other model

        messages = self.get_conversation_history()

        # convert conversation to OpenAI format
        messages_formatted = [{'role': message['role'], 'content': message['content']} for message in messages]

        response = openai.ChatCompletion.create(
            model=model,
            messages=messages_formatted,
            max_tokens=150
        )

        return {'role': bot_id, 'content': response['choices'][0]['message']['content']}
