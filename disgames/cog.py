from .mixins import TicTacToe, Hangman, MadLib, Chess
from discord.ext import commands

ALL_GAMES = [
    TicTacToe,
    Hangman,
    MadLib,
    Chess
]

class Games(commands.Cog, *ALL_GAMES):
    """
    This category provides awesome games like tictactoe, madlib and hangman!
    """
    def __init__(self, bot) -> None:
        super().__init__(bot)

def setup(bot: commands.Bot):
    bot.add_cog(Games(bot))
