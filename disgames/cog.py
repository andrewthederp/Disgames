from discord.ext import commands
from .constants import ALL_GAMES, BUTTON_GAMES
from .mixins import TicTacToeReactions

ALL_GAMES = [game for game in ALL_GAMES if game not in BUTTON_GAMES]
ALL_GAMES.remove(TicTacToeReactions)


class Games(*ALL_GAMES):
    """
    This category provides awesome games like tictactoe, madlib and hangman!
    """

    def __init__(self, bot):
        for cls in ALL_GAMES:
            cls.__init__(self, bot)


def setup(bot: commands.Bot):
    g = Games(bot)
    bot.add_cog(g)
