import akinator
import discord
from discord.ext import commands

try:
    class AkinButton(discord.ui.Button):
        def __init__(self, ctx, label):
            super().__init__(label=label, style=discord.ButtonStyle.primary if label not in ['end','back','yes'] else (discord.ButtonStyle.danger if label == 'end' else (discord.ButtonStyle.grey if label == 'back' else discord.ButtonStyle.green)))
            self.ctx = ctx

        async def callback(self, interaction):
            if interaction.user != self.ctx.author:
                return await interaction.response.send_message("It's not your turn", ephemeral=True)
            view = self.view
            if self.label == 'back':
                try:
                    view.q = view.aki.back()
                except akinator.CantGoBackAnyFurther:
                    pass
            elif self.label == 'end':
                view.clear_items()
                view.stop()
            else:
                view.q = view.aki.answer(self.label)

            if view.aki.progression > 80:
                view.aki.win()
                view.clear_items()
                em = discord.Embed(title=f"It's {view.aki.first_guess['name']}", description=f"({view.aki.first_guess['description']})!", color=discord.Color.blurple()).set_thumbnail(url=view.aki.first_guess['absolute_picture_path'])
                await interaction.response.edit_message(embed=em, view=view)
                view.stop()
            else:
                await interaction.response.edit_message(content=f"{interaction.user.mention}: **#{view.aki.step+1}.** {view.q}", view=view)

    class AkinView(discord.ui.View):
        def __init__(self,ctx,aki,q):
            super().__init__(timeout=None)
            for label in ['yes','probably','idk','probably not','no','back','end']:
                self.add_item(AkinButton(ctx, label))
            self.aki = aki
            self.q = q

    class AkinatorButtons(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        @commands.command('akinator')
        async def akinator_(self, ctx):
            aki = akinator.Akinator()
            q = aki.start_game(child_mode=True)
            await ctx.send(f"{ctx.author.mention}: **#{aki.step+1}.** {q}", view=AkinView(ctx,aki,q))

except AttributeError:
    class AkinatorButtons:
        pass