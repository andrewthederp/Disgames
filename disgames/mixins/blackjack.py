import discord
from discord.ext import commands
import random

class BlackJack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_lost(self, amt):
        if amt == 21:
            return False
        elif amt > 21:
            return True

    @commands.command(aliases=['bj'])
    async def blackjack(self, ctx):
        num = random.randint(1,10)
        bot_am = random.randint(1,10)
        hum_am = num
        embed = discord.Embed(title='BlackJack', color=discord.Color.blurple())
        embed.add_field(name=self.bot.user.display_name, value="`???`")
        embed.add_field(name=ctx.author.display_name, value="`"+str(hum_am)+"`")
        msg = await ctx.send(embed=embed)
        for _ in range(5):
            await msg.edit(f"You got {num}",embed=embed)
            inp = await self.bot.wait_for('message', check = lambda m:m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['hit','sit','h','s'])
            if inp.content.lower() in ['hit','h']:
                num = random.randint(1,10)
                bot_am += random.randint(1,10)
                hum_am += num
                bot_has_lost = self.has_lost(bot_am)
                hum_has_lost = self.has_lost(hum_am)
                embed._fields[1]['value'] = "`"+str(hum_am)+"`"
                if bot_has_lost:
                    embed._fields[0]['value'] = "`"+str(bot_am)+"`"
                    return await ctx.send("The bot went over 21", embed=embed)
                elif bot_has_lost == False:
                    embed._fields[0]['value'] = "`"+str(bot_am)+"`"
                    return await ctx.send("The bot hit 21", embed=embed)
                if hum_has_lost:
                    embed._fields[0]['value'] = "`"+str(bot_am)+"`"
                    return await ctx.send("You went over 21", embed=embed)
                elif hum_has_lost == False:
                    embed._fields[0]['value'] = "`"+str(bot_am)+"`"
                    return await ctx.send("You hit 21", embed=embed)
            else:
                embed._fields[0]['value'] = "`"+str(bot_am)+"`"
                if bot_am == hum_am:
                    return await ctx.send("Tie", embed=embed)
                elif bot_am > hum_am:
                    return await ctx.send("The bot won",embed=embed)
                else:
                    return await ctx.send("You won",embed=embed)
        embed._fields[0]['value'] = "`"+str(bot_am)+"`"
        await ctx.send("You won",embed=embed)