import akinator
import discord
from discord.ext import commands

class Akinator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command('akinator')
    async def akinator_(self, ctx):
        aki = akinator.Akinator()
        q = aki.start_game(child_mode=True)
        msg = await ctx.send(f"{ctx.author.mention}: **#{aki.step+1}.** {q}\nYes, No, I don't know, Probably, Probably not, Back, End")
        while aki.progression <= 80:
            i = aki.step
            await msg.edit(f"{ctx.author.mention}: **#{i+1}.** {q}\nYes, No, I don't know, Probably, Probably not, Back, End")
            inp = await self.bot.wait_for('message', check = lambda m:m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['yes','probably','idk','probably not','no','back','end'])
            try:
                await inp.delete()
            except discord.Forbidden:
                pass
            if inp.content.lower() == 'end':
                return await ctx.send("Ended the game")
            elif inp.content.lower() == 'back':
                try:
                    q = aki.back()
                except akinator.CantGoBackAnyFurther:
                    pass
            else:
                try:
                    q = aki.answer(inp.content.lower())
                except akinator.InvalidAnswerError:
                    pass
        aki.win()
        em = discord.Embed(title=f"It's {aki.first_guess['name']}", description=f"{aki.first_guess['description']}!", color=ctx.author.color)
        em.set_thumbnail(url=aki.first_guess['absolute_picture_path'])
        await ctx.send(embed=em)