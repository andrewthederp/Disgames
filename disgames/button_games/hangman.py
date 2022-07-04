import discord
import random

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

		if inp in view.guesses:
			embed = discord.Embed(title='Hangman', description=view.make_hangman()+f"\n\n{view.revealed_word}", color=ongoing_game_color)
			view.show_guesses(embed)
			return await interaction.response.edit_message(embed=embed, view=view)

		if inp == view.word:
			view.winner = True
			view.stop()
			view.clear_items()
			embed = discord.Embed(title='Hangman', description=view.make_hangman()+f"\n\n{''.join(f':regional_indicator_{i}:' for i in view.word)}", color=won_game_color)
			return await interaction.response.edit_message(content='You won!', embed=embed, view=view)
		else:
			if len(inp) == 1:
				if inp in view.word:
					view.revealed_word = list(view.revealed_word)
					for num, letter in enumerate(view.word):
						if letter == inp:
							view.revealed_word[num] = f":regional_indicator_{letter}:"
					view.revealed_word = ''.join(view.revealed_word)
					if '🟦' not in view.revealed_word:
						view.winner = True
						view.stop()
						view.clear_items()
						embed = discord.Embed(title='Hangman', description=view.make_hangman()+f"\n\n{''.join(f':regional_indicator_{i}:' for i in view.word)}", color=won_game_color)
						return await interaction.response.edit_message(content='You won!', embed=embed, view=view)
				else:
					view.errors += 1
				view.guesses.append(inp)
			else:
				view.errors += 1
		if view.errors == 6:
			view.winner = False
			view.stop()
			view.clear_items()
			embed = discord.Embed(title='Hangman', description=view.make_hangman()+f"\n\n{''.join(f':regional_indicator_{i}:' for i in view.word)}", color=lost_game_color)
			await interaction.response.edit_message(content='You lost', embed=embed, view=view)
		else:
			embed = discord.Embed(title='Hangman', description=view.make_hangman()+f"\n\n{view.revealed_word}", color=ongoing_game_color)
			view.show_guesses(embed)
			await interaction.response.edit_message(embed=embed, view=view)

class HangmanView(discord.ui.View):
	def __init__(self, ctx, word, end_game_option):
		super().__init__()
		self.guesses = []
		self.errors = 0
		self.word = word
		self.revealed_word = '🟦'*len(self.word)
		self.ctx = ctx
		self.winner = 0
		if end_game_option:
			button = discord.ui.Button(emoji='⏹', style=discord.ButtonStyle.danger)
			button.callback = self.end_game
			self.add_item(button)


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

	@discord.ui.button(label='Guess', style=discord.ButtonStyle.blurple)
	async def guess(self, interaction, button):
		await interaction.response.send_modal(HangmanModal(button))

	async def end_game(self, interaction):
		self.winner = False
		self.stop()
		for child in self.children:
			child.disabled = True
		embed = discord.Embed(title='Hangman', description=self.make_hangman()+f"\n\n{''.join(f':regional_indicator_{i}:' for i in self.word)}", color=lost_game_color)
		await interaction.response.edit_message(content='Game ended', embed=embed, view=self)

	async def interaction_check(self, interaction):
		if self.ctx.author == interaction.user:
			return True
		await interaction.response.send_message(content='This is not your game', ephemeral=True)


class Hangman:
	def __init__(self, ctx, *, min=3, max=7, word=None):

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
		self.revealed_word = '🟦'*len(self.word)

	
	async def start(self, *, end_game_option=False):
		view = HangmanView(self.ctx, self.word, end_game_option)
		embed = discord.Embed(title='Hangman', description=view.make_hangman()+f"\n\n{view.revealed_word}", color=ongoing_game_color)
		await self.ctx.send(embed=embed, view=view)
		await view.wait()
		return view.winner
