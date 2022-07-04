import discord
import random

class MinesweeperModal(discord.ui.Modal, title='Minesweeper'):
	def __init__(self, button):
		super().__init__()
		self.button = button

	inp = discord.ui.TextInput(
		label='coordinates',
		placeholder='Type your coordinates here...'
	)

	async def on_submit(self, interaction):
		inp = self.inp.value.lower()
		view = self.button.view
		for coor in inp.split(' '):
			coors = view.get_coors(coor)
			if coors:
				x,y = coors
				if self.button.label == 'reveal':
					block = view.board[x][y]
					if block == 'b':
						view.reveal_all()
						view.visible_board[x][y] = 'B'
						view.winner = False
						view.stop()
						embed = discord.Embed(title='Minesweeper', description=view.format_board()+f'\n\nFlags: `{view.flags}`', color=lost_game_color)
						return await interaction.response.edit_message(content='You lost!', embed=embed)
					elif block == 0:
						view.reveal_zeros(x, y)
					else:
						if view.visible_board[x][y] == 'f':
							view.flags += 1
						view.visible_board[x][y] = block
				else:
					block = view.visible_board[x][y]
					if block == ' ':
						view.flags -= 1
						view.visible_board[x][y] = 'f'

				if view.has_won():
					view.reveal_all()
					view.winner = True
					view.stop()
					embed = discord.Embed(title='Minesweeper', description=view.format_board()+f'\n\nFlags: `{view.flags}`', color=won_game_color)
					return await interaction.response.edit_message(content='You won!', embed=embed)
		embed = discord.Embed(title='Minesweeper', description=view.format_board()+f'\n\nFlags: `{view.flags}`', color=ongoing_game_color)
		await interaction.response.edit_message(embed=embed)

class MinesweeperView(discord.ui.View):
	def __init__(self, ctx, end_game_option, chance, format_dict):
		super().__init__()
		self.default_format_dict = {
								"b": "💣",
								"f": "🚩",
								" ": "🟦",
								"0": "⬛",
								"10": "🔟",
								"x":"❌",
								'B':"💥"
		}
		self.format_dict = format_dict
		self.ctx = ctx
		self.end_game_option = end_game_option
		self.chance = chance
		self.board, self.visible_board = self.create_boards()
		self.flags = len(list(self.get_bombs()))
		self.winner = 0
		if end_game_option:
			button = discord.ui.Button(emoji='⏹', style=discord.ButtonStyle.danger)
			button.callback = self.end_game
			self.add_item(button)

	async def interaction_check(self, interaction):
		if self.ctx.author == interaction.user:
			return True
		await interaction.response.send_message(content='This is not your game', ephemeral=True)

	async def end_game(self, interaction):
		self.winner = False
		self.stop()
		for child in self.children:
			child.disabled = True
		embed = discord.Embed(title='Minesweeper', description=self.format_board()+f'\nFlags: `{self.flags}`', color=lost_game_color)
		await interaction.response.edit_message(content='Game ended', embed=embed, view=self)

	def get_neighbours(self, x, y):
		for x_ in [x - 1, x, x + 1]:
			for y_ in [y - 1, y, y + 1]:
				if x_ != -1 and x_ != 11 and y_ != -1 and y_ != 11:
					yield x_, y_

	def format_board(self):
		for i in range(1, 10):
			self.default_format_dict[str(i)] = f"{i}\N{variation selector-16}\N{combining enclosing keycap}"
		lst = [":stop_button::regional_indicator_a::regional_indicator_b::regional_indicator_c::regional_indicator_d::regional_indicator_e::regional_indicator_f::regional_indicator_g::regional_indicator_h::regional_indicator_i::regional_indicator_j:"]
		for num, row in enumerate(self.visible_board, start=1):
			lst.append(self.default_format_dict[str(num)]+''.join([self.format_dict.get(str(column), self.default_format_dict.get(str(column), column)) for column in row]))
		return "\n".join(lst)

	def get_coors(self, coordinate):
		if len(coordinate) not in (2, 3):
			return None

		coordinate = coordinate.lower()
		if coordinate[0].isalpha():
			digit = coordinate[1:]
			letter = coordinate[0]
		else:
			digit = coordinate[:-1]
			letter = coordinate[-1]

		if not digit.isdecimal():
			return None

		x = int(digit) - 1
		y = ord(letter) - ord("a")

		if (not x in range(10)) or (not y in range(10)):
			return None
		return x, y

	def has_won(self):

		num = 0
		bombs = list(self.get_bombs())
		for x, row in enumerate(self.board):
			for y, column in enumerate(row):
				if str(self.visible_board[x][y]) == str(column):
					num += 1
		if num == ((len(self.board) * len(self.board[0])) - len(bombs)):
			return True

		for bomb in bombs:
			if not self.visible_board[bomb[0]][bomb[1]] == "f":
				return False
		if self.flags > -1:
			return True

	def reveal_all(self):
		for x in range(len(self.visible_board)):
			for y in range(len(self.visible_board[x])):
				if self.visible_board[x][y] == " ":
					self.visible_board[x][y] = self.board[x][y]
				elif self.visible_board[x][y] == 'f':
					if not self.board[x][y] == 'b':
						self.visible_board[x][y] = 'x'

	def reveal_zeros(self, x, y):
		for x_, y_ in self.get_neighbours(x, y):
			try:
				if self.visible_board[x_][y_] != " ":
					continue
				self.visible_board[x_][y_] = str(self.board[x_][y_])
				if self.board[x_][y_] == 0:
					self.reveal_zeros(x_, y_)
			except IndexError:
				pass

	def create_boards(self):
		board = [
			["b" if random.random() <= self.chance else "n" for _ in range(10)]
			for _ in range(10)
		]
		board[random.randint(0, 9)][random.randint(0, 9)] = "n"
		for x, row in enumerate(board):
			for y, cell in enumerate(row):
				if cell == "n":
					bombs = 0
					for x_, y_ in self.get_neighbours(x, y):
						try:
							if board[x_][y_] == "b":
								bombs += 1
						except IndexError:
							pass
					board[x][y] = bombs

		visible_board = [[" " for _ in range(10)] for _ in range(10)]
		return board, visible_board

	def get_bombs(self):
		lst = []
		for x in range(len(self.board)):
			for y in range(len(self.board[x])):
				if self.board[x][y] == "b":
					yield x,y

	@discord.ui.button(label='reveal', style=discord.ButtonStyle.blurple)
	async def reveal(self, interaction, button):
		await interaction.response.send_modal(MinesweeperModal(button))

	@discord.ui.button(label='flag', style=discord.ButtonStyle.danger)
	async def flag(self, interaction, button):
		await interaction.response.send_modal(MinesweeperModal(button))


class Minesweeper:
	def __init__(self, ctx, *, chance=.14, format_dict={}):

		from .. import ongoing_game_color, lost_game_color, won_game_color
		global ongoing_game_color, lost_game_color, won_game_color

		self.ctx = ctx
		self.chance = chance
		self.format_dict = format_dict

	async def start(self, *, end_game_option=True):
		view = MinesweeperView(self.ctx, end_game_option, self.chance, self.format_dict)
		embed = discord.Embed(title='Minesweeper', description=view.format_board()+f'\n\nFlags: `{view.flags}`', color=ongoing_game_color)
		view.msg = await self.ctx.send(embed=embed, view=view)
		await view.wait()
		return view.winner

