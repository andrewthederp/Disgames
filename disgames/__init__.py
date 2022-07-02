from .errors import PathNotFound
from .mixins import *
from typing import NamedTuple
import discord

resend_embed_list = ['re-send','resend']
end_game_list = ['end','stop','quit']

ongoing_game_color = discord.Color.blurple()
lost_game_color = discord.Color.red()
won_game_color = discord.Color.green()
drawn_game_color = discord.Color.red()

__title__ = 'disgames'
__author__ = 'andrewthederp'
__license__ = 'Apache License 2.0'
__copyright__ = 'Copyright 2021-2022 Andrewthederp and MarzaElise'
__version__ = '3.0.0'

class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
