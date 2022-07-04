import discord
import random

class Minesweeper:
	def __init__(self, ctx, *, chance=.14, format_dict={}):

		from .. import resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color
		global resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color

		self.ctx = ctx
		self.chance = chance
		self.format_dict = format_dict
		self.default_format_dict = {
								"b": "💣",
								"f": "🚩",
								" ": "🟦",
								"0": "⬛",
								"10": "🔟",
								"x":"❌",
								'B':"💥"
		}
		self.board, self.visible_board = self.create_boards()
		self.mode = 'reveal'
		self.flags = len(list(self.get_bombs()))

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

	async def start(self, *, delete_input=True, resend_embed_option=False, end_game_option=False):
		embed = discord.Embed(title='Minesweeper', description=self.format_board()+f'\n\nMode: `{self.mode}`\nFlags: `{self.flags}`', color=ongoing_game_color)
		self.msg = await self.ctx.send(embed=embed)
		while True:
			embed = discord.Embed(title='Minesweeper', description=self.format_board()+f'\n\nMode: `{self.mode}`\nFlags: `{self.flags}`', color=ongoing_game_color)
			await self.msg.edit(embed=embed)
			inp = await self.ctx.bot.wait_for('message', check=lambda m: m.author == self.ctx.author and m.channel == self.ctx.channel)
			if delete_input:
				try:
					await inp.delete()
				except discord.Forbidden:
					pass

			if resend_embed_option and inp.content.lower() in resend_embed_list:
				embed = discord.Embed(title='Minesweeper', description=self.format_board()+f'\n\nMode: `{self.mode}`\nFlags: `{self.flags}`', color=ongoing_game_color)
				self.msg = await self.ctx.send(embed=embed)
			elif end_game_option and inp.content.lower() in end_game_list:
				embed = discord.Embed(title='Minesweeper', description=self.format_board()+f'\n\nMode: `{self.mode}`\nFlags: `{self.flags}`', color=lost_game_color)
				await self.msg.edit(content='Game ended', embed=embed)
				self.winner = False
				break

			for coor in inp.content.split(' '):
				if coor.lower() in ['reveal','r']:
					self.mode = 'reveal'
					continue
				elif coor.lower() in ['flag','f']:
					self.mode = 'flag'
					continue

				coors = self.get_coors(coor)
				if coors:
					x,y = coors
					if self.mode == 'reveal':
						block = self.board[x][y]
						if block == 'b':
							self.reveal_all()
							self.visible_board[x][y] = 'B'
							embed = discord.Embed(title='Minesweeper', description=self.format_board()+f'\n\nMode: `{self.mode}`\nFlags: `{self.flags}`', color=lost_game_color)
							await self.msg.edit(content='You lost!', embed=embed)
							self.winner = False
							break
						elif block == 0:
							self.reveal_zeros(x, y)
						else:
							if self.visible_board[x][y] == 'f':
								self.flags += 1
							self.visible_board[x][y] = block
					else:
						block = self.visible_board[x][y]
						if block == ' ':
							self.flags -= 1
							self.visible_board[x][y] = 'f'

					if self.has_won():
						self.reveal_all()
						embed = discord.Embed(title='Minesweeper', description=self.format_board()+f'\n\nMode: `{self.mode}`\nFlags: `{self.flags}`', color=won_game_color)
						await self.msg.edit(content='You won!', embed=embed)
						self.winner = True
						break
		return self.winner