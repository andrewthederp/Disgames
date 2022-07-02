import akinator
import discord
from discord.ext import commands

class Akinator:
    def __init__(self, ctx, *, child_mode=True, controls=None, language=None):

        from .. import won_game_color
        global won_game_color

        self.ctx = ctx
        self.child_mode = child_mode
        self.aki = akinator.Akinator()
        self.language = language
        self.controls = controls or {'1️⃣':'0', '2️⃣':'1', '3️⃣':'2', '4️⃣':'3', '5️⃣':'4', '🏳':'end', '⬅':'back'}

    async def start(self, *, remove_reaction=False):
        q = self.aki.start_game(child_mode=self.child_mode, language=self.language)

        self.msg = await self.ctx.send(f"{self.ctx.author.mention}: **#{self.aki.step+1}.** {q}\nYes, No, I don't know, Probably, Probably not, Back")

        for emoji in list(self.controls.keys()):
            await self.msg.add_reaction(emoji)

        while self.aki.progression <= 80:
            await self.msg.edit(content=f"{self.ctx.author.mention}: **#{self.aki.step+1}.** {q}\nYes, No, I don't know, Probably, Probably not, Back")
            r, _ = await self.ctx.bot.wait_for('reaction_add', check = lambda r, u: u == self.ctx.author and str(r) in list(self.controls.keys()) and r.message == self.msg)
            if remove_reaction:
                try:
                    await self.msg.remove_reaction(r.emoji, self.ctx.author)
                except discord.Forbidden:
                    pass

            inp = self.controls[str(r)]
            if inp == 'end':
                return await self.ctx.send("Ended the game")
            elif inp == 'back':
                try:
                    q = self.aki.back()
                except akinator.CantGoBackAnyFurther:
                    pass
            else:
                try:
                    q = self.aki.answer(inp)
                except akinator.InvalidAnswerError:
                    pass
        self.aki.win()
        em = discord.Embed(title=f"It's {self.aki.first_guess['name']}", description=f"{self.aki.first_guess['description']}!", color=won_game_color)
        em.set_thumbnail(url=self.aki.first_guess['absolute_picture_path'])
        await self.ctx.send(embed=em)