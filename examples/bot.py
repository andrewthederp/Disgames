from discord.ext import commands
from disgames import register_commands
import discord

client = commands.Bot(command_prefix='your bot prefix', intents=discord.Intents.all())

register_commands(client)


client.run('your token here')