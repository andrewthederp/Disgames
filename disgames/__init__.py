from .board import Board
from .ttt import TicTacToe
from .hangman import Hangman
from .madlib import MadLib

all_games = [TicTacToe,Hangman,MadLib]

def register_commands(bot, *, ignore: list = []):
    for cls in all_games:
        if cls in ignore:
            continue
        else:
            bot.add_command(cls().command)
