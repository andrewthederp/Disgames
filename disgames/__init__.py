from .cog import *
from .constants import *
from discord.ext import commands
from .errors import PathNotFound
from .mixins import TicTacToe, TicTacToeReactions
from typing import NamedTuple
buttons = False
try:
    from discord.ui import Button
    from discord.ui import View
    buttons = True
except ImportError:
    pass


__title__ = 'disgames'
__author__ = 'andrewthederp'
__license__ = 'Apache License 2.0'
__copyright__ = 'Copyright 2021-2022 Andrewthederp and MarzaElise'
__version__ = '2.3.1'

async def register_commands(
    bot, *, ignore: list = [], stockfish_path=None, ttt_reactions=False, button_commands=True
):
    games = []
    if button_commands and buttons:
        ignore.extend(NON_BUTTON_GAMES)
    else:
        ignore.extend(BUTTON_GAMES)
    if ttt_reactions:
        ignore.append(TicTacToe)
        ignore.append(TicTacToeButtons)
        games.append(TicTacToeReactions)
    games += [game for game in ALL_GAMES if game not in ignore]

    class Games(*games):
        def __init__(self, bot):
            for cls in games:
                cls.__init__(self, bot)

    g = Games(bot)
    if stockfish_path:
        g.stockfish_path = stockfish_path
    await bot.add_cog(g)

class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
