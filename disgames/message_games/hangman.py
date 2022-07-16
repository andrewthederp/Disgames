import discord
import random


from .. import FormatType
try:
	import format_game
	better_formatting = True
except ImportError:
	better_formatting = False

class Hangman:
	def __init__(self, ctx, *, min=3, max=7, word=None, format_type=FormatType.text, dead_face=False):

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
		self.format_type = format_type
		self.dead_face = dead_face

		self.winner = 0

	def make_hangman(self):
		if not better_formatting or self.format_type == FormatType.text:
			head = "()" if self.errors > 0 else "  "
			torso = "||" if self.errors > 1 else "  "
			left_arm = "/" if self.errors > 2 else " "
			right_arm = "\\" if self.errors > 3 else " "
			left_leg = "/" if self.errors > 4 else " "
			right_leg = "\\" if self.errors > 5 else " "
			return (
				f"```\n {head}\n{left_arm}{torso}{right_arm}\n {left_leg}{right_leg}\n```"
			)
		else:
			import io
			arr = io.BytesIO()
			im = format_game.format_hangman_game(self.errors, image=True, dead_face=self.dead_face)
			im.save(arr, format='PNG')
			file = discord.File(arr, filename='Hangman.png')
			return file

	async def handle_embed(self, embed_color, send_or_edit='edit', content=''):
		formatted_game = self.make_hangman()
		if self.format_type == FormatType.image:
			embed = discord.Embed(title='Hangman', description=f"\n\n{self.revealed_word}", color=embed_color)
			self.show_guesses(embed)
			embed.set_image(url="attachment://Hangman.png")

			if send_or_edit == 'send':
				self.msg = await self.ctx.send(content=content, embed=embed, file=formatted_game)
			else:
				await self.msg.edit(content=content, embed=embed, attachments=[formatted_game])
		else:
			embed = discord.Embed(title='Hangman', description=self.make_hangman()+f"\n\n{self.revealed_word}", color=embed_color)
			self.show_guesses(embed)

			if send_or_edit == 'send':
				self.msg = await self.ctx.send(content=content, embed=embed)
			else:
				await self.msg.edit(content=content, embed=embed)

	def show_guesses(self, embed):
		if self.guesses:
			embed.add_field(name="Guesses", value="".join(f":regional_indicator_{i}:" for i in self.guesses),inline=False)
	
	async def start(self, *, delete_input=False, resend_embed_option=False, end_game_option=False):
		await self.handle_embed(ongoing_game_color, 'send')
		while self.errors < 6:
			await self.handle_embed(ongoing_game_color, 'edit')
			inp = await self.ctx.bot.wait_for('message', check=lambda m:m.author==self.ctx.author and m.channel==self.ctx.channel and (m.content.isalpha() or m.content.lower()=='re-send'))

			if delete_input:
				try:
					await inp.delete()
				except discord.Forbidden:
					pass

			if inp.content.lower() in self.guesses:
				continue
			if inp.content.lower() == self.word:
				await self.handle_embed(won_game_color, 'edit', 'You won!')
				return True

			elif resend_embed_option and inp.content.lower() in resend_embed_list:
				await self.handle_embed(ongoing_game_color, 'send')
			elif end_game_option and inp.content.lower() in end_game_list:
				await self.handle_embed(lost_game_color, 'edit', 'Game ended')
				return False
			else:
				if len(inp.content.lower()) == 1:
					if inp.content.lower() in self.word:
						self.revealed_word = list(self.revealed_word)
						for num, letter in enumerate(self.word):
							if letter == inp.content.lower():
								self.revealed_word[num] = f":regional_indicator_{letter}:"
						self.revealed_word = ''.join(self.revealed_word)
						if '🟦' not in self.revealed_word:
							await self.handle_embed(won_game_color, 'edit', 'You won!')
							return True
					else:
						self.errors += 1
					self.guesses.append(inp.content.lower())
				else:
					self.errors += 1
		await self.handle_embed(lost_game_color, 'edit', 'You lost')
		return False
