import os
import discord
from discord import Intents, app_commands
from dotenv import load_dotenv
import openai

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Make sure to set this environment variable

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
openai.api_key = OPENAI_API_KEY

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await tree.sync()  # Sync global slash commands

@tree.command()
@app_commands.describe(message='The message to echo back')
async def winfo(interaction: discord.Interaction, message: str):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=message,
        max_tokens=150
    )
    await interaction.response.send_message(response.choices[0].text.strip())

client.run(DISCORD_TOKEN)
