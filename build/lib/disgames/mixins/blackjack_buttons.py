import discord
from discord.ext import commands
import random

try:
    class BJButton(discord.ui.Button):
        def __init__(self, label, style, ctx):
            super().__init__(label=label,style=style)
            self.ctx = ctx

        async def callback(self, interaction):
            if interaction.user != self.ctx.author:
                return await interaction.response.send_message("It's not your turn", ephemeral=True)
            view = self.view
            view.times += 1
            content = ''
            gameover = False
            if self.label == 'Hit':
                num = random.randint(1,10)
                view.bot_am += random.randint(1,10)
                view.hum_am += num
                bot_has_lost = view.has_lost(view.bot_am)
                hum_has_lost = view.has_lost(view.hum_am)
                view.embed._fields[1]['value'] = '`'+str(view.hum_am)+'`'
                content += 'You got '+str(num)
                if bot_has_lost:
                    gameover = True
                    view.end_view()
                    view.embed._fields[0]['value'] = '`'+str(view.bot_am)+'`'
                    content += '\nThe bot went over 21'
                elif bot_has_lost == False:
                    gameover = True
                    view.end_view()
                    view.embed._fields[0]['value'] = '`'+str(view.bot_am)+'`'
                    content += '\nThe bot hit 21'
                if hum_has_lost:
                    gameover = True
                    view.end_view()
                    view.embed._fields[0]['value'] = '`'+str(view.bot_am)+'`'
                    content += '\nYou went over 21'
                elif hum_has_lost == False:
                    gameover = True
                    content += '\nYou hit 21'
                    view.end_view()
                    view.embed._fields[0]['value'] = '`'+str(view.bot_am)+'`'
            else:
                gameover = True
                view.end_view()
                view.embed._fields[0]['value'] = '`'+str(view.bot_am)+'`'
                if view.bot_am == view.hum_am:
                    content = 'Tie'
                elif view.bot_am > view.hum_am:
                    content = 'The bot won'
                else:
                    content = 'You won'
            if not gameover and view.times == 5:
                view.embed._fields[0]['value'] = '`'+str(view.bot_am)+'`'
                view.end_view()
                return await interaction.response.edit_message(content='You won', embed=view.embed, view=view)
            await interaction.response.edit_message(content=content, embed=view.embed, view=view)

    class BJView(discord.ui.View):
        def __init__(self, embed, bot_am, hum_am, ctx):
            super().__init__(timeout=None)
            self.add_item(BJButton('Hit', discord.ButtonStyle.success, ctx))
            self.add_item(BJButton('Stand', discord.ButtonStyle.grey, ctx))
            self.bot_am = bot_am
            self.hum_am = hum_am
            self.times = 0
            self.embed = embed

        def has_lost(self, amt):
            if amt == 21:
                return False
            elif amt > 21:
                return True

        def end_view(self):
            self.clear_items()
            self.stop()

    class BlackJackButtons(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        @commands.command(aliases=['bj'])
        async def blackjack(self, ctx):
            bot_am = random.randint(1,10)
            hum_am = random.randint(1,10)
            embed = discord.Embed(title='BlackJack', color=discord.Color.blurple())
            embed.add_field(name=bot.user.display_name, value="`???`")
            embed.add_field(name=ctx.author.display_name, value="`"+str(hum_am)+"`")
            await ctx.send(embed=embed, view=BJView(embed, bot_am, hum_am, ctx))

except AttributeError:
    class BlackJackButtons:
        pass