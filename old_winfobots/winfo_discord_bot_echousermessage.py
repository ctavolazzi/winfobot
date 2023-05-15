import os
import discord
from discord import Intents, app_commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await tree.sync()  # Sync global slash commands

@tree.command()
@app_commands.describe(message='The message to echo back')
async def winfo(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(f"You said: {message}")

client.run(DISCORD_TOKEN)
