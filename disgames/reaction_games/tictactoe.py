import discord

class TicTacToe:
	def __init__(self, ctx, *, x, o, controls=None, format_dict={}):

		from .. import ongoing_game_color, lost_game_color, won_game_color, drawn_game_color
		global ongoing_game_color, lost_game_color, won_game_color, drawn_game_color

		self.x                   = x
		self.o                   = o
		self.ctx                 = ctx
		self.turn                = x
		self.board               = [[' ' for _ in range(3)] for _ in range(3)]
		self.controls            = controls or {'↖':(0,0), '⬆':(0,1), '↗':(0,2), '⬅':(1,0), '⏺':(1,1), '➡':(1,2), '↙':(2,0), '⬇':(2,1), '↘':(2,2), '🏳':'stop'}
		self.conversion          = {x:'x',o:'o'}
		self.format_dict         = format_dict
		self.default_format_dict = {
									' ':'⬛',
									'x':'❌',
									'o':'⭕'
									}

	def format_board(self):
		lst = []
		for row in self.board:
			lst.append("".join(
				[self.format_dict.get(i, self.default_format_dict.get(i,i)) for i in row]
			))
		return "\n".join(lst)

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

	async def start(self, *, remove_reaction=False):
		embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}\n{self.format_board()}", color=ongoing_game_color)
		self.msg = await self.ctx.send(embed=embed)
		for emoji in list(self.controls.keys()):
			await self.msg.add_reaction(emoji)
		while True:
			r,u = await self.ctx.bot.wait_for('reaction_add', check=lambda r,u: r.message == self.msg and r.emoji in list(self.controls.keys()))

			if remove_reaction:
				try:
					await r.message.remove_reaction(r.emoji,u)
				except discord.Fobidden:
					pass
				await r.message.remove_reaction(r.emoji,self.ctx.bot.user)

			inp = self.controls[r.emoji]

			if inp == 'stop':
				embed = discord.Embed(title='Tic Tac Toe', description=f"Game ended by: {u.mention}\n{self.format_board()}", color=lost_game_color)
				return await self.msg.edit(content=f'Game ended!', embed=embed)

			if u == self.turn:
				x,y = inp
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
				self.controls.pop(r.emoji)
				await r.message.remove_reaction(r.emoji,self.ctx.bot.user)
