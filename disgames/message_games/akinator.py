import akinator
import discord
from discord.ext import commands

class Akinator:
	def __init__(self, ctx, *, child_mode=True, language=None):

		from .. import resend_embed_list, end_game_list, won_game_color
		global resend_embed_list, end_game_list, won_game_color

		self.ctx = ctx
		self.child_mode = child_mode
		self.language = language
		self.language = language
		self.aki = akinator.Akinator()

	async def start(self, *, delete_input=False, end_game_option=False, resend_embed_option=False):
		q = self.aki.start_game(child_mode=self.child_mode, language=self.language)

		controls = ['yes','probably','idk','probably not','no','back']
		controls.extend(resend_embed_list)
		controls.extend(end_game_list)

		self.msg = await self.ctx.send(f"{self.ctx.author.mention}: **#{self.aki.step+1}.** {q}\nYes, No, I don't know, Probably, Probably not, Back")
		while self.aki.progression <= 80:
			await self.msg.edit(content=f"{self.ctx.author.mention}: **#{self.aki.step+1}.** {q}\nYes, No, I don't know, Probably, Probably not, Back")
			inp = await self.ctx.bot.wait_for('message', check = lambda m:m.author == self.ctx.author and m.channel == self.ctx.channel and m.content.lower() in controls)
			if delete_input:
				try:
					await inp.delete()
				except discord.Forbidden:
					pass
			if end_game_option and inp.content.lower() in end_game_list:
				return await self.ctx.send("Ended the game")
			elif resend_embed_option and inp.content.lower() in resend_embed_list:
				self.msg = await self.ctx.send(f"{self.ctx.author.mention}: **#{self.aki.step+1}.** {q}\nYes, No, I don't know, Probably, Probably not, Back")
			if inp.content.lower() == 'back':
				try:
					q = self.aki.back()
				except akinator.CantGoBackAnyFurther:
					pass
			else:
				try:
					q = self.aki.answer(inp.content.lower())
				except akinator.InvalidAnswerError:
					pass
		self.aki.win()
		em = discord.Embed(title=f"It's {self.aki.first_guess['name']}", description=f"{self.aki.first_guess['description']}!", color=won_game_color)
		em.set_thumbnail(url=self.aki.first_guess['absolute_picture_path'])
		await self.ctx.send(embed=em)