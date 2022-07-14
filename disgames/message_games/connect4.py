import discord

class Connect4:
	def __init__(self, ctx, *, red, blue, format_dict={}):

		from .. import resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color, drawn_game_color
		global resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color, drawn_game_color

		self.ctx = ctx
		self.board = [[' ' for _ in range(7)] for _ in range(6)]
		self.turn = 'r'
		self.turns = {'r':red,'b':blue}
		self.format_dict = format_dict
		self.default_format_dict = {
								"r": "🔴",
								"b": "🔵",
								" ": "⬛",
								"R": "♦️",
								"B": "🔷"
		}
		self.winner = 0

	def format_board(self):
		lst = []
		for row in self.board:
			lst.append(''.join([self.format_dict.get(i, self.default_format_dict.get(i,i)) for i in row]))
		return '\n'.join(lst)+'\n1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣'

	def move(self, index):
		if self.board[0][index] != ' ':
			return None
		for y in range(0, 6):
			if self.board[5-y][index] == ' ':
				self.board[5-y][index] = self.turn
				break
		return True

	def has_won(self):
		height = 6
		width = 7
		for x in range(height):
			for y in range(width - 3):
				if (self.board[x][y] == self.board[x][y + 1] and self.board[x][y] == self.board[x][y + 2] and self.board[x][y] == self.board[x][y + 3] and self.board[x][y] != " "):
					self.board[x][y] = self.board[x][y].upper()
					self.board[x][y + 1] = self.board[x][y].upper()
					self.board[x][y + 2] = self.board[x][y].upper()
					self.board[x][y + 3] = self.board[x][y].upper()
					return True, "in a horizontal row"
		for x in range(height - 3):
			for y in range(width):
				if (self.board[x][y] == self.board[x + 1][y] and self.board[x][y] == self.board[x + 2][y] and self.board[x][y] == self.board[x + 3][y] and self.board[x][y] != " "):
					self.board[x][y] = self.board[x][y].upper()
					self.board[x + 1][y] = self.board[x][y].upper()
					self.board[x + 2][y] = self.board[x][y].upper()
					self.board[x + 3][y] = self.board[x][y].upper()
					return True, "in a vertical row"
		for x in range(height - 3):
			for y in range(width - 3):
				if (self.board[x][y] == self.board[x + 1][y + 1] and self.board[x][y] == self.board[x + 2][y + 2] and self.board[x][y] == self.board[x + 3][y + 3] and self.board[x][y] != " "):
					self.board[x][y] = self.board[x][y].upper()
					self.board[x + 1][y + 1] = self.board[x][y].upper()
					self.board[x + 2][y + 2] = self.board[x][y].upper()
					self.board[x + 3][y + 3] = self.board[x][y].upper()
					return True, "on a \ diagonal"
		for x in range(height - 3):
			for y in range(3, width):
				if (self.board[x][y] == self.board[x + 1][y - 1] and self.board[x][y] == self.board[x + 2][y - 2] and self.board[x][y] == self.board[x + 3][y - 3] and self.board[x][y] != " "):
					self.board[x][y] = self.board[x][y].upper()
					self.board[x + 1][y - 1] = self.board[x][y].upper()
					self.board[x + 2][y - 2] = self.board[x][y].upper()
					self.board[x + 3][y - 3] = self.board[x][y].upper()
					return True, "in a / diagonal"
		if not sum([row.count(' ') for row in self.board]):
			return False
		return None

	async def start(self, *, delete_input=False, end_game_option=False, resend_embed_option=False):
		embed = discord.Embed(title='Connect4', description = f'Turn: {self.turns[self.turn].mention}\n'+self.format_board(), color=ongoing_game_color)
		self.msg = await self.ctx.send(embed=embed)
		while True:
			inp = await self.ctx.bot.wait_for('message', check=lambda m:m.channel == self.ctx.channel and m.author in list(self.turns.values()))
			if delete_input:
				try:
					await inp.delete()
				except discord.Forbidden:
					pass

			if end_game_option and inp.content.lower() in end_game_list:
				embed = discord.Embed(title='Connect4', description=f'Game ended by: {inp.author.mention}\n'+self.format_board(), color=lost_game_color)
				await self.msg.edit(content='Game ended!', embed=embed)
				self.winner = self.turns['r'] if self.turns['b'] == inp.author else self.turns['b']
				break
			elif resend_embed_option and inp.content.lower() in resend_embed_list:
				embed = discord.Embed(title='Connect4', description = f'Turn: {self.turns[self.turn].mention}\n'+self.format_board(), color=ongoing_game_color)
				self.msg = await self.ctx.send(embed=embed)
				continue

			if inp.content.isdigit() and int(inp.content)-1 in range(7) and inp.author == self.turns[self.turn]:
				done = self.move(int(inp.content)-1)
				if not done:
					continue
				won = self.has_won()
				if won != None:
					if won == False:
						embed = discord.Embed(title='Connect4', description=f'Turn: {self.turns[self.turn].mention}\n'+self.format_board(), color=drawn_game_color)
						await self.msg.edit(content='Tie!', embed=embed)
						self.winner = None
						break
					else:
						embed = discord.Embed(title='Connect4', description=f'Turn: {self.turns[self.turn].mention}\n'+self.format_board(), color=won_game_color)
						await self.msg.edit(content=f'{self.turns[self.turn].mention} connected 4 {won[1]}', embed=embed)
						self.winner = self.turns[self.turn]
						break
				self.turn = 'b' if self.turn == 'r' else 'r'
		return self.winner