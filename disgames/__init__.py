from discord.ext import commands
from .cog import *
from .constants import *

def register_commands(
    bot,
    *,
    ignore: list = []
):
    games = [
        game for game in ALL_GAMES if game not in ignore
    ]
    class Games(*games): ...
    bot.add_cog(Games(bot))
