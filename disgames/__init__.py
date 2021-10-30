from discord.ext import commands
from .cog import *

def register_commands(
    bot,
    # *,
    # ignore: list = []
):
    bot.add_cog(Games(bot))
    # for cls in ALL_GAMES:
    #     if cls not in ignore:
    #         bot.add_command(cls().command)
