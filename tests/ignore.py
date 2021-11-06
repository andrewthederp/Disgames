from disgames import Chess, register_commands
from discord.ext import commands

bot = commands.Bot("!", help_command=None)
register_commands(bot, ignore=[Chess])

assert len(bot.commands) == 3 # Madlib, ttt, hangman
