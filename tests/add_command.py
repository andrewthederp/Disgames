from disgames import TicTacToe
from discord.ext import commands

bot = commands.Bot("!", help_command=None)
bot.add_command(TicTacToe().command)
assert len(bot.commands) == 1  # only the tictactoe command
