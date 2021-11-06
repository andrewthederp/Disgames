# this file shows how you can use the register_commands function


from discord.ext import commands
from disgames import register_commands

bot = commands.Bot("!") # ! is the prefix

register_commands(bot)

# this by default would add all the commands to the bot inside a "Games" cog

# you can optionally use the `ignore` kwarg to have control over
# what commands would be added to the bot

from disgames import TicTacToe

register_commands(bot, ignore=[TicTacToe])

# now you would have all the other commands except TicTacToe
