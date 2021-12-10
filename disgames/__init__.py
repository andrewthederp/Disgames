from .cog import *
from .constants import *
from .errors import PathNotFound
from discord.ext import commands

def register_commands(bot, *, ignore: list = [], stockfish_path=None):
    games = [game for game in ALL_GAMES if game not in ignore]
    class Games(*games):
        def __init__(self, bot):
            for cls in games:
                cls.__init__(self, bot)
    g = Games(bot)
    if stockfish_path:
        g.stockfish_path = stockfish_path
    bot.add_cog(g)
