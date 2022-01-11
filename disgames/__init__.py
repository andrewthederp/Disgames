from .cog import *
from .constants import *
from discord.ext import commands
from .errors import PathNotFound
from .mixins import TicTacToe, TicTacToeReactions
from typing import NamedTuple


__title__ = 'disgames'
__author__ = 'andrewthederp'
__license__ = 'Apache License 2.0'
__copyright__ = 'Copyright 2021-2022 Andrewthederp and MarzaElise'
__version__ = '2.2.2'

def register_commands(
    bot, *, ignore: list = [], stockfish_path=None, ttt_reactions=False
):
    games = []
    if ttt_reactions:
        ignore.append(TicTacToe)
        games.append(TicTacToeReactions)
    games += [game for game in ALL_GAMES if game not in ignore]

    class Games(*games):
        def __init__(self, bot):
            for cls in games:
                cls.__init__(self, bot)

    g = Games(bot)
    if stockfish_path:
        g.stockfish_path = stockfish_path
    bot.add_cog(g)

class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
