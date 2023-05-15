import os
import discord
import json
from discord import Intents, app_commands
from dotenv import load_dotenv
import openai
import logging
import datetime
from collections import defaultdict, deque
import uuid

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Make sure to set this environment variable

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
openai.api_key = OPENAI_API_KEY

# Set up logging
logging.basicConfig(filename='winfobot.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Initialize user history, main log and the queue
user_history = defaultdict(list)
main_log = []
queue = deque(maxlen=20)

# Current date for the main log
current_date = datetime.date.today()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    logging.info(f'We have logged in as {client.user}')
    await tree.sync()  # Sync global slash commands

@tree.command()
@app_commands.describe(message='The message to chat with the bot')
async def winfo(interaction: discord.Interaction, message: str):
    try:
        await interaction.response.defer()  # Defer the initial response

        user_id = str(interaction.user.id)
        user_name = interaction.user.name.replace(" ", "_")  # To avoid issues with file naming
        timestamp = interaction.created_at.isoformat()
        message_id = interaction.id

        # Store user message in the history, main log, and the queue
        user_message = {"message_id": message_id, "username": user_name, "role": "user", "content": message, "time": timestamp}
        user_history[user_id].append(user_message)
        main_log.append(user_message)
        queue.append(user_message)

        # Call the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=list(queue)
        )

        # Store assistant message in the history, main log, and the queue
        ai_response = response.choices[0].message['content']
        ai_message_id = uuid.uuid4().hex  # Generate a unique ID for the AI's message
        ai_message = {"message_id": ai_message_id, "username": "Winfo", "role": "assistant", "content": ai_response, "time": timestamp}
        user_history[user_id].append(ai_message)
        main_log.append(ai_message)
        queue.append(ai_message)

        # Update user message and assistant message with ai_response
        user_message["ai_response"] = ai_response
        ai_message["ai_response"] = ai_response

        # Save user history
        with open(f"{user_name}_{user_id}_recent_history.json", "w") as f:
            json.dump({"category": user_history[user_id]}, f)

        # Check if the date has changed and if so, create a new main log file
        today = datetime.date.today()
        if today != current_date:
            current_date = today
            main_log = []

        # Save all messages in the main log file
        with open(f"{current_date}_main_log.json", "a") as f:
            json.dump({"category": main_log}, f)
            f.write('\n')  # For better readability of the log file

        # Save the queue
        with open("winfo_queue.json", "w") as f:
            json.dump({"category": list(queue)}, f)

        # Send the assistant's message to the chat
        await interaction.followup.send(f"{interaction.user.name} said: \n{message}\n\nWinfo: \n{ai_response}")  # Send the response
    except openai.error.RateLimitError:
        await interaction.followup.send("The bot is currently busy. Please try again later.")

client.run(DISCORD_TOKEN)

