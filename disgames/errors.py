import discord
from discord.ext import commands

class PathNotFound(commands.CommandError):
    def __init__(self):
        super().__init__("Couldn't find the path to your stockfish_20011801_32bit.exe\n\nPlease head to https://www.dropbox.com/sh/75gzfgu7qo94pvh/AADMl6xkjU9qdx-Q5xeUJMxba/Stockfish%2011?dl=0&subfolder_nav_tracking=1 to download stockfish")