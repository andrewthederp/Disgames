import discord

class TicTacToe:
	def __init__(self, ctx, *, x, o, format_dict={}):

		from .. import resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color, drawn_game_color
		global resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color, drawn_game_color

		self.x                   = x
		self.o                   = o
		self.ctx                 = ctx
		self.turn                = x
		self.board               = [[' ' for _ in range(3)] for _ in range(3)]
		self.conversion          = {x:'x',o:'o'}
		self.format_dict         = format_dict
		self.default_format_dict = {
									' ':'⬛',
									'x':'❌',
									'o':'⭕'
									}

	def format_board(self):
		lst = ["⏹:regional_indicator_a::regional_indicator_b::regional_indicator_c:"]
		numbers = {1:'1️⃣',2:'2️⃣',3:'3️⃣'}
		for x, row in enumerate(self.board, start=1):
			lst.append(numbers[x]+"".join(
				[self.format_dict.get(i, self.default_format_dict.get(i,i)) for i in row]
			))
		return "\n".join(lst)

	def get_coors(self, coordinate):
		if len(coordinate) != 2:
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

		if (not x in range(3)) or (not y in range(3)):
			return None
		return x, y

	def has_won(self):
		BLANK = " "
		for i in range(3):

			if (self.board[i][0] == self.board[i][1] == self.board[i][2]) and self.board[i][0] != BLANK:
				return True
			if (self.board[0][i] == self.board[1][i] == self.board[2][i]) and self.board[0][i] != BLANK:
				return True

		if (self.board[0][0] == self.board[1][1] == self.board[2][2]) and self.board[0][0] != BLANK:
			return True

		if (self.board[0][2] == self.board[1][1] == self.board[2][0]) and self.board[0][2] != BLANK:
			return True
		if sum([i.count(BLANK) for i in self.board]) == 0:
			return False
		return None

	async def start(self, *, delete_input=False, resend_embed_option=False):
		embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}\n{self.format_board()}", color=ongoing_game_color)
		self.msg = await self.ctx.send(embed=embed)
		while True:
			msg = await self.ctx.bot.wait_for('message', check=lambda m:m.author==self.turn and m.channel==self.ctx.channel)

			if delete_input:
				try:
					await msg.delete()
				except discord.Forbidden:
					pass

			if resend_embed_option and msg.content.lower() in resend_embed_list:
				embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}\n{self.format_board()}", color=ongoing_game_color)
				self.msg = await self.ctx.send(embed=embed)
				continue
			elif msg.content.lower() in end_game_list:
				embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}\n{self.format_board()}", color=lost_game_color)
				return await self.msg.edit(content=f'Game ended!', embed=embed)

			coors = self.get_coors(msg.content)
			if coors and self.board[coors[0]][coors[1]] == ' ':
				x,y = coors
				self.board[x][y] = self.conversion[self.turn]
				won = self.has_won()
				if won == True:
					embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}\n{self.format_board()}", color=won_game_color)
					return await self.msg.edit(content=f'{self.turn.mention} won!', embed=embed)
				elif won == False:
					embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}\n{self.format_board()}", color=drawn_game_color)
					return await self.msg.edit(content=f'Draw', embed=embed)
				else:
					self.turn = self.x if self.turn == self.o else self.o
					embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}\n{self.format_board()}", color=ongoing_game_color)
					await self.msg.edit(embed=embed)
