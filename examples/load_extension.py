# this file shows how you could use load_extension to add games
# to your bot

# first, we make the bot

from discord.ext import commands

bot = commands.Bot("!") # Here, ! is the prefix

bot.load_extension("disgames")

# this would add a "Games" cog to your bot with all the games in it