# this file shows how you could use Bot.add_cog to add games to your bot

# first, create the bot instance
from discord.ext import commands

bot = commands.Bot("!") # ! is the prefix in this case

# now import the game you need

from disgames import Hangman

bot.add_cog(Hangman(bot))

# if you need 2 or more commands only, consider using the register_commands function instead