from bot import Bot
import secrets
from port import ConnectionRequest

class BotManager:
    def __init__(self):
        self.bots = {}

    def create_bot(self, bot_id, port):
        bot = Bot(port)
        self.bots[bot_id] = bot
        return bot

    def start_bot(self, bot_id):
        bot = self.bots.get(bot_id)
        if bot:
            bot.brain.start_thinking()
        else:
            raise ValueError(f"No bot with id {bot_id} exists")

    def stop_bot(self, bot_id):
        bot = self.bots.get(bot_id)
        if bot:
            bot.brain.stop_thinking()
        else:
            raise ValueError(f"No bot with id {bot_id} exists")

    def teach_bot(self, bot_id, behavior):
        bot = self.bots.get(bot_id)
        if bot:
            bot.learn(behavior)
        else:
            raise ValueError(f"No bot to teach")

    def execute_command(self, bot_id, command, *args):
        bot = self.bots.get(bot_id)
        if bot:
            bot.execute(command, *args)
        else:
            raise ValueError(f"No bot with id {bot_id} exists")

    def remove_bot(self, bot_id):
        bot = self.bots.get(bot_id)
        if bot:
            bot.brain.stop_thinking()
            del self.bots[bot_id]
        else:
            raise ValueError(f"No bot with id {bot_id} exists")

class ConnectionManager:
    def __init__(self, port):
        self.port = port
        self.connections = set()

    async def connect(self, target):
        if target in self.connections:
            raise ConnectionError(f"{target.__class__.__name__ + ' ' + target.id} is already connected to Port {self.port.address}")
        elif target is None:
            raise ConnectionError(f"Cannot connect None to Port {self.port.address}.")
        elif target is self.port:
            raise ConnectionError(f"Cannot connect Port {self.port.address} to itself.")
        else:
            # Create a connection request with a token
            token = secrets.token_hex(16)
            request = ConnectionRequest(self.port, token)
            if await target.handle_connection_request(request):
                self.connections.add(target)
                self.port.logger.info(f"{target.__class__.__name__ + ' ' + target.id} has been connected to Port {self.port.address}")
            else:
                raise ConnectionError(f"Could not connect {target.__class__.__name__ + ' ' + target.id} to Port {self.port.address}.")
        return self

    async def disconnect(self, target):
        if target in self.connections:
            self.connections.remove(target)
            self.port.logger.info(f"{target.__class__.__name__ + ' ' + target.id} has been disconnected from Port {self.port.address}")
        else:
            raise ConnectionError(f"{target.__class__.__name__ + ' ' + target.id} is not connected to Port {self.port.address}")
        return self

