import os
import discord
from discord import Intents, app_commands
from dotenv import load_dotenv
import openai
import logging
from datetime import datetime
import uuid
import json

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
openai.api_key = OPENAI_API_KEY

# Set up logging
logging.basicConfig(filename='winfobot.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Global message queue and history
message_que = []
message_history = []

# Load message history and queue from files
def load_message_history():
    try:
        with open('message_history.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def load_message_que():
    try:
        with open('message_que.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

message_history = load_message_history()
message_que = load_message_que()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    logging.info(f'We have logged in as {client.user}')
    await tree.sync()  # Sync global slash commands

@tree.command()
@app_commands.describe(message='The message to chat with the bot')
async def winfo(interaction: discord.Interaction, message: str):
    global message_history, message_que
    try:
        await interaction.response.defer()  # Defer the initial response
        logging.info(f'Received message from {interaction.user.name} (ID: {interaction.user.id})')

        # Create the message object and add it to the global queue
        message_object = {
            "message_id": str(uuid.uuid4()),
            "user_id": interaction.user.id,
            "username": interaction.user.name,
            "role": "user",
            "content": message,
            "time": str(datetime.now())
        }

        message_history.append(message_object)

        if len(message_que) > 50:
            message_que.pop(0)

        message_que.append(message_object)

        logging.info(f'Added message to queue: {message_object}')

        # Build the message context api array
        message_context = []
        for message in message_que:
            api_message = {
                "role": message['role'],
                "content": message['content']
            }
            message_context.append(api_message)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message_context,
        )

        ai_response = response.choices[0].message['content']
        logging.info(f'Response from OpenAI: {ai_response}')

        # Build the response message object and add it to the message history
        response_object = {
            "message_id": str(uuid.uuid4()),
            "user_id": interaction.user.id,
            "username": interaction.user.name,
            "role": "assistant",
            "content": ai_response,
            "time": str(datetime.now())
        }

        message_history.append(response_object)

        logging.info(f'Added response to history: {response_object}')

        # Write the updated message history and queue to their respective files
        with open('message_history.json', 'w') as f:
            json.dump(message_history, f)
        with open('message_que.json', 'w') as f:
            json.dump(message_que, f)

        await interaction.followup.send(f"{interaction.user.name} said: \n{message['content']}\n\nWinfo: \n{ai_response}")  # Send the response
        logging.info('Sent response to user')

    except openai.error.RateLimitError:
        await interaction.followup.send("The bot is currently busy. Please try again later.")
        logging.error("Rate limit error occurred.")
    except Exception as e:
        await interaction.followup.send(f"An unexpected error occurred: {type(e).__name__}, {e}")
        logging.error(f"An unexpected error occurred: {type(e).__name__}, {e}")

client.run(DISCORD_TOKEN)
