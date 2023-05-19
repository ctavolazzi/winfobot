from bot import Bot
from conversation import Conversation
import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

# Add a way to test the bot
def test_bot(bot):
    for ability in bot.abilities.values():
        ability.test_self()
    bot.test_self()

# Test
if __name__ == '__main__':
    bot1 = Bot("bot1")
    bot2 = Bot("bot2")

    conversation = Conversation(openai_api_key)
    conversation.add_bot(bot1)
    conversation.add_bot(bot2)

    system = {'role': 'system', 'content': 'system', 'source': 'system'}

    conversation.add_and_broadcast_message(system, "You are now chatting with another bot. Please identify yourself and ask a question, then wait for a response.")

    count = 0

    while count < 10:
        bot1.speak(conversation)
        bot2.speak(conversation)
        count += 1
