import discord
import random

class Hangman:
	def __init__(self, ctx, *, min=3, max=7, word=None):

		from .. import resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color
		global resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color

		path = '/'.join(__file__.split('/')[:-2])
		self.ctx = ctx
		words = []
		for word_ in open(f'{path}/assets/words.txt').readlines():
			word_ = word_.replace('\r','').strip()
			if len(word_) >= min and len(word_) <= max and word_.isalpha():
				words.append(word_)
		self.word = word or random.choice(words)
		self.word = self.word.lower()
		self.revealed_word = '🟦'*len(self.word)
		self.guesses = []
		self.errors = 0

	def make_hangman(self):
		head = "()" if self.errors > 0 else "  "
		torso = "||" if self.errors > 1 else "  "
		left_arm = "/" if self.errors > 2 else " "
		right_arm = "\\" if self.errors > 3 else " "
		left_leg = "/" if self.errors > 4 else " "
		right_leg = "\\" if self.errors > 5 else " "
		return (
			f"```\n {head}\n{left_arm}{torso}{right_arm}\n {left_leg}{right_leg}\n```"
		)

	def show_guesses(self, embed):
		if self.guesses:
			embed.add_field(name="Guesses", value="".join(f":regional_indicator_{i}:" for i in self.guesses),inline=False)
	
	async def start(self, *, delete_input=False, resend_embed_option=False, end_game_option=False):
		embed = discord.Embed(title='Hangman', description=self.make_hangman()+f"\n\n{self.revealed_word}", color=ongoing_game_color)
		self.msg = await self.ctx.send(embed=embed)
		while self.errors < 6:
			embed = discord.Embed(title='Hangman', description=self.make_hangman()+f"\n\n{self.revealed_word}", color=ongoing_game_color)
			self.show_guesses(embed)
			await self.msg.edit(embed=embed)
			inp = await self.ctx.bot.wait_for('message', check=lambda m:m.author==self.ctx.author and m.channel==self.ctx.channel and (m.content.isalpha() or m.content.lower()=='re-send'))
			if delete_input:
				try:
					await inp.delete()
				except discord.Forbidden:
					pass
			if inp.content.lower() in self.guesses:
				continue
			if inp.content.lower() == self.word:
				embed = discord.Embed(title='Hangman', description=self.make_hangman()+f"\n\n{''.join(f':regional_indicator_{i}:' for i in self.word)}", color=won_game_color)
				return await self.msg.edit(content='You won!', embed=embed)
			elif resend_embed_option and inp.content.lower() in resend_embed_list:
				embed = discord.Embed(title='Hangman', description=self.make_hangman()+f"\n\n{self.revealed_word}", color=ongoing_game_color)
				self.msg = await self.ctx.send(embed=embed)
			elif end_game_option and inp.content.lower() in end_game_list:
				embed = discord.Embed(title='Hangman', description=self.make_hangman()+f"\n\n{''.join(f':regional_indicator_{i}:' for i in self.word)}", color=lost_game_color)
				return await self.msg.edit(content='Game ended', embed=embed)
			else:
				if len(inp.content.lower()) == 1:
					if inp.content.lower() in self.word:
						self.revealed_word = list(self.revealed_word)
						for num, letter in enumerate(self.word):
							if letter == inp.content.lower():
								self.revealed_word[num] = f":regional_indicator_{letter}:"
						self.revealed_word = ''.join(self.revealed_word)
						if '🟦' not in self.revealed_word:
							embed = discord.Embed(title='Hangman', description=self.make_hangman()+f"\n\n{self.revealed_word}", color=won_game_color)
							return await self.msg.edit(content='You won!', embed=embed)
					else:
						self.errors += 1
					self.guesses.append(inp.content.lower())
				else:
					self.errors += 1
		embed = discord.Embed(title='Hangman', description=self.make_hangman()+f"\n\n{''.join(f':regional_indicator_{i}:' for i in self.word)}", color=lost_game_color)
		await self.msg.edit(content='You lost', embed=embed)
