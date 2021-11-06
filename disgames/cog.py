from discord.ext import commands
from .constants import ALL_GAMES

class Games(*ALL_GAMES):
    """
    This category provides awesome games like tictactoe, madlib and hangman!
    """
    def __init__(self, bot) -> None:
        super().__init__(bot)

def setup(bot: commands.Bot):
    bot.add_cog(Games(bot))
