from .board import Board
from .ttt import TicTacToe

all_games = [TicTacToe]


def register_commands(bot, *, ignore: list = []):
    for cls in all_games:
        if cls in ignore:
            continue
        else:
            bot.add_command(cls().command)
