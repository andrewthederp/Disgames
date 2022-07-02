import discord

class Connect4:
	def __init__(self, ctx, *, red, blue, format_dict={}, controls=None):

		from .. import resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color, drawn_game_color
		global resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color, drawn_game_color

		self.ctx = ctx
		self.board = [[' ' for _ in range(7)] for _ in range(6)]
		self.turn = 'r'
		self.controls = controls or {'1️⃣':0,'2️⃣':1,'3️⃣':2,'4️⃣':3,'5️⃣':4,'6️⃣':5,'7️⃣':6,"🏳":'stop'}
		self.turns = {'r':red,'b':blue}
		self.format_dict = format_dict
		self.default_format_dict = {
								"r": "🔴",
								"b": "🔵",
								" ": "⬛",
								"R": "♦️",
								"B": "🔷"
		}

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

	async def start(self, *, remove_reaction=False):
		embed = discord.Embed(title='Connect4', description = f'Turn: {self.turns[self.turn].mention}\n'+self.format_board(), color=ongoing_game_color)
		self.msg = await self.ctx.send(embed=embed)
		for emoji in list(self.controls.keys()):
			await self.msg.add_reaction(emoji)
		while True:
			r, u = await self.ctx.bot.wait_for('reaction_add', check=lambda r,u:m.message == self.msg and u in list(self.turns.values()) and str(r) in list(self.controls.keys()))
			if remove_reaction:
				try:
					await self.msg.remove_reaction(r.emoji, u)
				except discord.Forbidden:
					pass
				await r.message.remove_reaction(r.emoji,self.ctx.bot.user)

			inp = self.controls[r.emoji]

			if inp == 'stop':
				embed = discord.Embed(title='Connect4', description=f'Game ended by: {u.mention}\n'+self.format_board(), color=lost_game_color)
				return await self.msg.edit(content='Game ended!', embed=embed)

			if u == self.turns[self.turn]:
				done = self.move(inp)
				if not done:
					continue
				won = self.has_won()
				if won != None:
					if won == False:
						embed = discord.Embed(title='Connect4', description=f'Turn: {self.turns[self.turn].mention}\n'+self.format_board(), color=drawn_game_color)
						await self.msg.edit(content='Tie!', embed=embed)
						break
					else:
						embed = discord.Embed(title='Connect4', description=f'Turn: {self.turns[self.turn].mention}\n'+self.format_board(), color=won_game_color)
						await self.msg.edit(content=f'{self.turns[self.turn].mention} connected 4 {won[1]}', embed=embed)
						break
				self.turn = 'b' if self.turn == 'r' else 'r'