import discord
from discord.ext import commands
from discord import app_commands
import os
from keep_alive import keep_alive

token = os.environ['ETHERYA']
bot = commands.Bot(command_prefix="+", intents=intents)
intents = discord.Intents.default()
intents.message_content = True
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Bot connecté en tant que {bot.user}')

keep_alive()
bot.run(token)
