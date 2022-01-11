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

###########################################################################

from discord.ext import commands
from disgames import register_commands

bot = commands.Bot("!") # ! is the prefix

register_commands(bot, stockfish_path='Path\\to\\stockfish_20011801_32bit.exe') # by providing the stockfish_path it'll attempt to use it for the chess ai

###########################################################################

from discord.ext import commands
from disgames import register_commands

bot = commands.Bot("!") # ! is the prefix

register_commands(bot, ttt_reactions=True) # ttt_reactions is False by default, by setting it to True it will add a version of ttt which uses reactions instead of the normal version
