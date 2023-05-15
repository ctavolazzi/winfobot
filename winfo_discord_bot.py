import os
import discord
import json
from discord import Intents
from dotenv import load_dotenv
import openai
import logging
import datetime
from collections import defaultdict


load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Make sure to set this environment variable

intents = discord.Intents.default()
client = discord.Client(intents=intents)
openai.api_key = OPENAI_API_KEY

# Set up logging
logging.basicConfig(filename='winfobot.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# A dictionary to keep the recent history of each user
user_history = defaultdict(list)

# Current date for the main log
current_date = datetime.date.today()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$winfo'):
        # Get the user's message
        user_message = message.content[7:]
        user_id = str(message.author.id)
        user_name = message.author.name.replace(" ", "_")  # To avoid issues with file naming
        timestamp = message.created_at.isoformat()

        # Store user message in the history
        user_history[user_id].append({"message_id": message.id, "time": timestamp, "role": "user", "content": user_message})

        # Call the OpenAI API
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=user_history[user_id]
            )
            # Store assistant message in the history
            ai_response = response.choices[0].message['content']
            user_history[user_id].append({"message_id": message.id, "time": timestamp, "role": "assistant", "content": ai_response})

            # Save user history
            with open(f"{user_name}_{user_id}_recent_history.json", "w") as f:
                json.dump(user_history[user_id], f)

            # Check if the date has changed and if so, create a new main log file
            today = datetime.date.today()
            if today != current_date:
                current_date = today

            # Save all messages in the main log file
            with open(f"{current_date}_main_log.json", "a") as f:
                json.dump({"username": user_name, "message_id": message.id, "time": timestamp, "role": "user", "content": user_message, "ai_response": ai_response}, f)
                f.write('\n')  # For better readability of the log file

            # Send the assistant's message to the chat
            await message.channel.send(ai_response)
        except openai.error.RateLimitError:
            await message.channel.send("The bot is currently busy. Please try again later.")
        except Exception as e:
            await message.channel.send(f"An unexpected error occurred: {type(e).__name__}, {e}")
            logging.error(f"An unexpected error occurred: {type(e).__name__}, {e}")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    logging.info(f'We have logged in as {client.user}')

client.run(DISCORD_TOKEN)
