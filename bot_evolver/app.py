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

    system_message = {'role': 'system', 'content': "You are now chatting with another bot. Please identify yourself and ask a question, then wait for a response.", 'source': 'system'}

    conversation.add_and_broadcast_message(system_message)

    count = 0

    while count < 10:
        bot1_message = bot1.generate_message(conversation)
        bot2_message = bot2.generate_message(conversation)

        bot1.speak(bot1_message['content'])
        bot2.speak(bot2_message['content'])
        count += 1
