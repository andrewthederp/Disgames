import discord
from discord.ext import commands
import aiohttp

class MadLib(commands.Cog):
    """
    Madlib command
    """
    def __init__(self, bot) -> None:
        self.bot = bot

    @property
    def url(self):
        return "http://madlibz.herokuapp.com/api/random"

    @property
    def session(self):
        return self.bot.http._HTTPClient__session

    async def request(self, min: int, max: int):
        params = {"minlength": min, "maxlength": max}
        response = await self.session.get(self.url, params=params)
        return await response.json()

    @commands.command()
    async def madlib(self, ctx, min: int = 5, max: int = 25):
        json = await self.request(min, max)
        lst = []
        try:
            for question in json["blanks"]:
                await ctx.reply(f"Please send: {question}", mention_author=False)
                answer = await ctx.bot.wait_for(
                    "message",
                    check=lambda m: m.author == ctx.author
                    and m.channel == ctx.channel,
                )
                lst.append(answer.content)
            madlib = json["value"]
            string = " ".join(
                f'{madlib[i]}{lst[i] if len(lst)-1 >= i else ""}'
                for i in range(len(madlib) - 1)
            )
            # I dont understand this shit bruh - Marcus
            # H good - Andreaw

            await ctx.send(string)
        except KeyError:
            return await ctx.send(f"Invalid syntax: invalid arguments entered")