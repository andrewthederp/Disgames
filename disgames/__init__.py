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

def enable_better_formatting():
    import os
    os.system('pip install git+https://github.com/andrewthederp/FormatGame')
    try:
        import format_game
        return 1
    except ImportError:
        return 2

class FormatType:
    plain = 0
    plain_codeblock = 1

    listed = 2
    listed_codeblock = 3

    emojis = 4
    emojis_codeblock = 5

    image = 6

    text = 7

class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
