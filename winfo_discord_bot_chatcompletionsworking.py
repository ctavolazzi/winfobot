import os
import discord
from discord import Intents, app_commands
from dotenv import load_dotenv
import openai
import logging

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

conversations = {}  # Dictionary to store conversation history

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    logging.info(f'We have logged in as {client.user}')
    await tree.sync()  # Sync global slash commands

@tree.command()
@app_commands.describe(message='The message to chat with the bot')
async def winfo(interaction: discord.Interaction, message: str):
    user_id = interaction.user.id
    if user_id not in conversations:
        # Start a new conversation
        conversations[user_id] = [{"role": "system", "content": "You are a helpful assistant."}]
    # Add the user's message to the conversation
    conversations[user_id].append({"role": "user", "content": message})
    logging.info(f'Received message: {message}')
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversations[user_id]
    )
    # Add the assistant's response to the conversation
    conversations[user_id].append({"role": "assistant", "content": response.choices[0].message['content']})
    logging.info(f'Sending response: {response.choices[0].message["content"]}')
    await interaction.response.send_message(response.choices[0].message['content'])

client.run(DISCORD_TOKEN)
