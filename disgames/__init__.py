from .board import Board
from .ttt import TTT
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord.ext import commands

all_games = [TTT]


def register_commands(bot: commands.Bot, *, ignore: list = []):
    for cls in all_games:
        if cls in ignore:
            continue
        else:
            bot.add_command(cls().command)
