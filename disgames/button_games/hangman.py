import discord
import random

from .. import FormatType
try:
	import format_game
	better_formatting = True
except ImportError:
	better_formatting = False


class HangmanModal(discord.ui.Modal, title='Hangman'):
	def __init__(self, button):
		super().__init__()
		self.button = button

	inp = discord.ui.TextInput(
		label='Guess',
		placeholder='Type your guess here...'
	)

	async def on_submit(self, interaction):
		inp = self.inp.value.lower()
		view = self.button.view
		await interaction.response.defer()

		if inp in view.guesses:
			# embed = discord.Embed(title='Hangman', description=view.make_hangman()+f"\n\n{view.revealed_word}", color=ongoing_game_color)
			# view.show_guesses(embed)
			# return await interaction.response.edit_message(embed=embed, view=view)
			return

		if inp == view.word:
			view.winner = True
			view.stop()
			view.clear_items()
			return await view.handle_embed(won_game_color, 'edit', 'You won!', ''.join(f':regional_indicator_{i}:' for i in view.word))
			# embed = discord.Embed(title='Hangman', description=view.make_hangman()+f"\n\n{''.join(f':regional_indicator_{i}:' for i in view.word)}", color=won_game_color)
			# return await interaction.response.edit_message(content='You won!', embed=embed, view=view)
		else:
			if len(inp) == 1:
				if inp in view.word:
					view.revealed_word = list(view.revealed_word)
					for num, letter in enumerate(view.word):
						if letter == inp:
							view.revealed_word[num] = letter
					view.revealed_word = ''.join(view.revealed_word)
					if ' ' not in view.revealed_word:
						view.winner = True
						view.stop()
						view.clear_items()
						return await view.handle_embed(won_game_color, 'edit', 'You won!', ''.join(f':regional_indicator_{i}:' for i in view.word))
						# embed = discord.Embed(title='Hangman', description=view.make_hangman()+f"\n\n{''.join(f':regional_indicator_{i}:' for i in view.word)}", color=won_game_color)
						# return await interaction.response.edit_message(content='You won!', embed=embed, view=view)
				else:
					view.errors += 1
				view.guesses.append(inp)
			else:
				view.errors += 1
		if view.errors == 6:
			view.winner = False
			view.stop()
			view.clear_items()
			return await view.handle_embed(lost_game_color, 'edit', 'You lost!', ''.join(f':regional_indicator_{i}:' for i in view.word))
			# embed = discord.Embed(title='Hangman', description=view.make_hangman()+f"\n\n{''.join(f':regional_indicator_{i}:' for i in view.word)}", color=lost_game_color)
			# await interaction.response.edit_message(content='You lost', embed=embed, view=view)
		else:
			return await view.handle_embed(ongoing_game_color, 'edit')
			# embed = discord.Embed(title='Hangman', description=view.make_hangman()+f"\n\n{view.revealed_word}", color=ongoing_game_color)
			# view.show_guesses(embed)
			# await interaction.response.edit_message(embed=embed, view=view)

class HangmanView(discord.ui.View):
	def __init__(self, ctx, word, end_game_option, format_type, dead_face):
		super().__init__()
		self.guesses = []
		self.errors = 0
		self.word = word
		self.revealed_word = ' '*len(self.word)
		self.ctx = ctx
		self.winner = 0

		self.format_type = format_type
		self.dead_face = dead_face

		if end_game_option:
			button = discord.ui.Button(emoji='⏹', style=discord.ButtonStyle.danger)
			button.callback = self.end_game
			self.add_item(button)


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

	async def handle_embed(self, embed_color, send_or_edit='edit', content='', description=''):
		formatted_game = self.make_hangman()
		print(formatted_game, self.format_type)
		if self.format_type == FormatType.image:
			embed = discord.Embed(title='Hangman', description=description or ''.join(f':regional_indicator_{i}:' if i != ' ' else '🟦' for i in self.revealed_word), color=embed_color)
			self.show_guesses(embed)
			# embed.set_image(url="attachment://Hangman.png")

			if send_or_edit == 'send':
				self.msg = await self.ctx.send(content=content, embed=embed, file=formatted_game, view=self)
			else:
				await self.msg.edit(content=content, embed=embed, attachments=[formatted_game], view=self)
		else:
			formatted_revealed_word = ''.join(f':regional_indicator_{i}:' if i != ' ' else '🟦' for i in self.revealed_word)
			embed = discord.Embed(title='Hangman', description=self.make_hangman()+f"\n\n{description or formatted_revealed_word}", color=embed_color)
			self.show_guesses(embed)

			if send_or_edit == 'send':
				self.msg = await self.ctx.send(content=content, embed=embed, view=self)
			else:
				await self.msg.edit(content=content, embed=embed, view=self)

	def show_guesses(self, embed):
		if self.guesses:
			embed.add_field(name="Guesses", value="".join(f":regional_indicator_{i}:" for i in self.guesses),inline=False)

	@discord.ui.button(label='Guess', style=discord.ButtonStyle.blurple)
	async def guess(self, interaction, button):
		await interaction.response.send_modal(HangmanModal(button))

	async def end_game(self, interaction):
		await interaction.response.defer()
		self.winner = False
		self.stop()
		for child in self.children:
			child.disabled = True
		await self.handle_embed(lost_game_color, 'edit', 'Game ended')
		# embed = discord.Embed(title='Hangman', description=self.make_hangman()+f"\n\n{''.join(f':regional_indicator_{i}:' for i in self.word)}", color=lost_game_color)
		# await interaction.response.edit_message(content='Game ended', embed=embed, view=self)

	async def interaction_check(self, interaction):
		if self.ctx.author == interaction.user:
			return True
		await interaction.response.send_message(content='This is not your game', ephemeral=True)


class Hangman:
	def __init__(self, ctx, *, min=3, max=7, word=None, format_type=FormatType.text, dead_face=False):

		from .. import ongoing_game_color, lost_game_color, won_game_color
		global ongoing_game_color, lost_game_color, won_game_color
	
		path = '/'.join(__file__.split('/')[:-2])
		self.ctx = ctx
		words = []
		for word_ in open(f'{path}/assets/words.txt').readlines():
			word_ = word_.replace('\r','').strip()
			if len(word_) >= min and len(word_) <= max and word_.isalpha():
				words.append(word_)
		self.word = word or random.choice(words)
		self.word = self.word.lower()

		self.format_type = format_type
		self.dead_face = dead_face

	
	async def start(self, *, end_game_option=False):
		view = HangmanView(self.ctx, self.word, end_game_option, self.format_type, self.dead_face)
		# embed = discord.Embed(title='Hangman', description=view.make_hangman()+f"\n\n{view.revealed_word}", color=ongoing_game_color)
		# await self.ctx.send(embed=embed, view=view)
		await view.handle_embed(ongoing_game_color, 'send')
		await view.wait()
		return view.winner
