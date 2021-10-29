from .board import Board
from .ttt import TicTacToe
from .hangman import Hangman
from .madlib import MadLib

ALL_GAMES = [TicTacToe, Hangman, MadLib]


def register_commands(bot, *, ignore: list = []):
    for cls in ALL_GAMES:
        if cls not in ignore:
            bot.add_command(cls().command)
