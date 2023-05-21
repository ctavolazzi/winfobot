from bot import Bot

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
