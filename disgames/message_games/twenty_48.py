import random, copy
import discord

class _2048:
	def __init__(self, ctx, *, end_num=2048):

		from .. import resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color
		global resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color

		self.ctx = ctx
		self.board = [[' ' for _ in range(4)] for _ in range(4)]

		if end_num not in [2**i for i in range(1, 15)]:
			raise
		self.end_num = end_num

		self.UP = (-1, 0)
		self.DOWN = (1, 0)
		self.LEFT = (0, -1)
		self.RIGHT = (0, 1)
		self.score = 0
		self.winner = 0

		self.conv = {'u':self.UP, 'd':self.DOWN, 'l':self.LEFT, 'r':self.RIGHT}

	def move(self, board, x, y, char, direction):
		try:
			x += direction[0]
			y += direction[1]
			if x < 0 or y < 0:
				return
			is_empty = board[x][y] == ' '
			if is_empty:
				board[x][y] = char
				board[x-direction[0]][y-direction[1]] = ' '
		except IndexError:
			pass

	def compress(self, board, direction):
		for _ in range(len(board)):
			for x, row in enumerate(board):
				for y, col in enumerate(row):
					if col != ' ':
						self.move(board, x, y, col, direction)

	def merge(self, board, direction):
		merges = []
		for x, row in enumerate(board):
			for y, col in enumerate(row):
				if not col == ' ':
					try:
						x_ = x + direction[0]
						y_ = y + direction[1]
						if x_ < 0 or y_ < 0:
							continue
						is_same = board[x_][y_] == col
						if is_same and (x, y) not in merges:
							merges.append((x_, y_))
							num = int(board[x][y])+int(board[x_][y_])
							self.score += num
							board[x_][y_] = str(num)
							board[x][y] = ' '
					except IndexError:
						continue

	def get_empty(self, board):
		for x, row in enumerate(board):
			for y, col in enumerate(row):
				if col == ' ':
					yield x, y

	def add_num(self, board):
		empties = list(self.get_empty(board))
		if empties:
			empty = random.choice(empties)
			board[empty[0]][empty[1]] = '2' if random.randint(1, 10) != 10 else '4'

	def format_board(self, board):
		lst = []
		for row in board:
			lst.append('['+', '.join(row)+']')
		return '\n'.join(lst)

	def checks(self, board):
		empties = list(self.get_empty(board))
		if not empties:
			board_copy = copy.deepcopy(board)
			for direction in list(self.conv.values()):
				self.compress(self.board, direction)
				self.merge(self.board, direction)
				self.compress(self.board, direction)
				if board != board_copy:
					self.board = board_copy
					return True
			self.board = board_copy
			return False
		return True

	def has_won(self, board):
		for row in board:
			for col in row:
				if col != ' ':
					if int(col) == self.end_num:
						return True


	async def start(self, *, delete_input=False, resend_embed_option=False, end_game_option=False):
		self.add_num(self.board)
		self.add_num(self.board)

		embed = discord.Embed(title='2048', description=f"Score: {self.score}\n\n```\n{self.format_board(self.board)}\n```", color=ongoing_game_color)
		self.msg = await ctx.send(embed=embed)

		while True:
			board_copy = copy.deepcopy(self.board)
			inp = await self.ctx.bot.wait_for('message', check=lambda m: m.author == self.ctx.author and m.channel == self.ctx.channel)

			if delete_input:
				try:
					await inp.delete()
				except discord.Forbidden:
					pass

			if resend_embed_option and msg.content.lower() in resend_embed_list:
				embed = discord.Embed(title='2048', description=f"Score: {self.score}\n\n```\n{self.format_board(self.board)}\n```", color=ongoing_game_color)
				self.msg = await ctx.send(embed=embed)
				continue
			elif end_game_option and msg.content.lower() in end_game_list:
				embed = discord.Embed(title='2048', description=f"Score: {self.score}\n\n```\n{self.format_board(self.board)}\n```", color=lost_game_color)
				await ctx.send(content='Game ended!', embed=embed)
				self.winner = False
				break

			if inp.content.lower() in list(self.conv.keys()):
				try:
					direction = self.conv[inp.content.lower()]
				except KeyError:
					continue
				self.compress(self.board, direction)
				self.merge(self.board, direction)
				self.compress(self.board, direction)

				if not board_copy == self.board:
					self.add_num(self.board)

				if self.has_won(self.board):
					embed = discord.Embed(title='2048', description=f"Score: {self.score}\n\n```\n{self.format_board(self.board)}\n```", color=won_game_color)
					await ctx.send(content='You won!', embed=embed)
					self.winner = True
					break
				elif not self.checks(self.board):
					embed = discord.Embed(title='2048', description=f"Score: {self.score}\n\n```\n{self.format_board(self.board)}\n```", color=lost_game_color)
					await ctx.send(content='You lost!', embed=embed)
					self.winner = False
					break

			embed = discord.Embed(title='2048', description=f"Score: {self.score}\n\n```\n{self.format_board(self.board)}\n```", color=ongoing_game_color)
			await self.msg.edit(embed=embed)
		return self.winner

await _2048(ctx).start()