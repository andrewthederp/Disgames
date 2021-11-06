from disgames import Chess
from discord.ext import commands

bot = commands.Bot("!", help_command=None)
bot.add_cog(Chess(bot))

assert len(bot.commands) == 1 # should only be the Chess command from the Chess cog
