import akinator
import discord
from discord.ext import commands

class AkinatorButton(discord.ui.Button):
	def __init__(self, label, emoji=None):
		super().__init__(label=label, style=discord.ButtonStyle.blurple)
		if emoji:
			self.emoji = emoji

	async def callback(self, interaction):
		view = self.view

		if self.emoji == '⬅':
			try:
				q = view.aki.back()
			except akinator.CantGoBackAnyFurther:
				pass
		else:
			q = view.aki.answer(self.label)

		if view.aki.progression <= 80:
			await interaction.response.edit_message(content=f"{interaction.user.mention}: **#{view.aki.step+1}.** {q}\nYes, No, I don't know, Probably, Probably not, Back")
		else:
			view.aki.win()
			em = discord.Embed(title=f"It's {view.aki.first_guess['name']}", description=f"{view.aki.first_guess['description']}!", color=won_game_color)
			em.set_thumbnail(url=view.aki.first_guess['absolute_picture_path'])
			await interaction.response.send_message(embed=em)
			view.stop()

class Akinator(discord.ui.View):
	def __init__(self, ctx, *, child_mode=True, language=None):
		super().__init__()

		from .. import won_game_color
		global won_game_color

		self.ctx = ctx
		self.child_mode = child_mode
		self.aki = akinator.Akinator()
		self.language = language

		for label in ["Yes", "No", "I don't know", "Probably", "Probably not"]:
			self.add_item(AkinatorButton(label))
		self.add_item(AkinatorButton('\u200b', '⬅'))
		self.winner = None

	async def end_game(self, interaction):
		self.stop()
		for child in self.children:
			child.disabled = True
		await interaction.response.send_message(content='Ended the game', view=self)

	async def interaction_check(self, interaction):
		if interaction.user != self.ctx.author:
			return await interaction.response.send_message(content='This is not your message', ephemeral=True)
		return True

	async def start(self, *, end_game_option=False):
		if end_game_option:
			button = discord.ui.Button(emoji='⏹', style=discord.ButtonStyle.danger)
			button.callback = self.end_game
			self.add_item(button)

		q = self.aki.start_game(child_mode=self.child_mode, language=self.language)
		self.msg = await self.ctx.send(f"{self.ctx.author.mention}: **#{self.aki.step+1}.** {q}\nYes, No, I don't know, Probably, Probably not, Back", view=self)
		await self.wait()
		return self.winner