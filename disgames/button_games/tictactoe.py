import discord

class TicTacToeButton(discord.ui.Button):
	def __init__(self, custom_id):
		super().__init__(custom_id=custom_id, label='\u200b', row=int(custom_id[0]))

	async def callback(self, interaction):
		view = self.view
		x = int(self.custom_id[0])
		y = int(self.custom_id[1])
		if view.turn == view.x:
			style = discord.ButtonStyle.danger
		else:
			style = discord.ButtonStyle.success
		view.board[x][y] = view.conversion[interaction.user]
		self.style = style
		self.disabled = True
		won = view.has_won()
		if won == True:
			for child in view.children:
				child.disabled = True
			await interaction.response.edit_message(content=f'{view.turn.mention} won!', view=view)
		elif won == False:
			for child in view.children:
				child.disabled = True
			await interaction.response.edit_message(content='Draw', view=view)
		else:
			view.turn = view.x if view.turn == view.o else view.o
			await interaction.response.edit_message(content=f"Turn: {view.turn.mention}", view=view)


class TicTacToeView(discord.ui.View):
	def __init__(self, ctx, x, o):
		super().__init__()
		self.x                   = x
		self.o                   = o
		self.ctx                 = ctx
		self.board               = [[' ' for _ in range(3)] for _ in range(3)]
		self.conversion          = {x:'x',o:'o'}
		self.turn                = x
		for x in range(3):
			for y in range(3):
				self.add_item(TicTacToeButton(str(x)+str(y)))

	async def interaction_check(self, interaction):
		if interaction.user not in list(self.conversion.keys()):
			await interaction.response.send_message(content="You're not in this game", ephemeral=True)
		elif interaction.user != self.turn:
			await interaction.response.send_message(content="It's not your turn", ephemeral=True)
		else:
			return True

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

class TicTacToe:
	def __init__(self, ctx, *, x, o):
		self.x           = x
		self.o           = o
		self.ctx         = ctx

	async def start(self):
		view = TicTacToeView(self.ctx, self.x, self.o)
		await self.ctx.send(content=f"Turn: {view.turn.mention}", view=view)