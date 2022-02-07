import discord
from discord.ext import commands
import random

try:
	class TicTacToeButton(discord.ui.Button):
		def __init__(self, ctx, x, y):
			super().__init__(style=discord.ButtonStyle.secondary, label=' ', row=y)
			self.x = x
			self.y = y
			self.ctx = ctx

		async def callback(self, interaction: discord.Interaction):
			view = self.view
			state = view.board[self.y][self.x]
			if state in ("X", "O"):
				return
			if interaction.user not in view.players:
				return await interaction.response.send_message("You aren't playing in this game", ephemeral=True)
			elif interaction.user != view.current_player:
				return await interaction.response.send_message("It's not your turn", ephemeral=True)

			if view.current_player == view.players[0]:
				self.style = discord.ButtonStyle.danger
				self.label = 'X'
				self.disabled = True
				view.board[self.y][self.x] = "X"
				view.current_player = view.players[1]
				content = "It is now O's turn"
			elif view.current_player == view.players[1]:
				self.style = discord.ButtonStyle.success
				self.label = 'O'
				self.disabled = True
				view.board[self.y][self.x] = "O"
				view.current_player = view.players[0]
				content = "It is now X's turn"

			winner = view.check_board_winner()
			if winner:
				if winner == 'tie':
					content = "It's a tie!"
				else:
					content = 'X won!!!' if view.current_player == view.players[1] else "O won!!!"

				for child in view.children:
					child.disabled = True

				view.stop()
				return await interaction.response.edit_message(content=content, view=view)

			if view.current_player == self.ctx.bot.user:
				button_to_coor = {'00':0, '01':3, '02':6, '10':1, '11':4, '12':7, "20":2, "21":5, "22":8}
				empty = view.get_empty_ttt(view.board)
				empty = random.choice(empty)
				coor = button_to_coor[empty[0]+empty[1]]
				for num, child in enumerate(view.children):
					if num == coor:
						child.style = discord.ButtonStyle.success
						child.label = 'O'
						child.disabled = True
						view.board[int(empty[0])][int(empty[1])] = "O"
						view.current_player = view.players[0]
						content = "It is now X's turn"
						break

			winner = view.check_board_winner()
			if winner:
				if winner == 'tie':
					content = "It's a tie!"
				else:
					content = 'X won!!!' if view.current_player == view.players[1] else "O won!!!"

				for child in view.children:
					child.disabled = True

				view.stop()

			await interaction.response.edit_message(content=content, view=view)

	class TicTacToe(discord.ui.View):
		def __init__(self, ctx, players):
			super().__init__(timeout=None)
			self.current_player = players[0]
			self.players = players
			self.board = [[0 for i in range(3)] for i in range(3)]
			for x in range(3):
				for y in range(3):
					self.add_item(TicTacToeButton(ctx, x, y))

		def check_board_winner(self):
			BLANK = 0
			bord = self.board
			for i in range(3):

				if (bord[i][0] == bord[i][1] == bord[i][2]) and bord[i][
					0
				] != BLANK:
					return True
				if (bord[0][i] == bord[1][i] == bord[2][i]) and bord[0][
					i
				] != BLANK:
					return True

			if (bord[0][0] == bord[1][1] == bord[2][2]) and bord[0][0] != BLANK:
				return True

			if (bord[0][2] == bord[1][1] == bord[2][0]) and bord[0][2] != BLANK:
				return True
			h = 0
			for i in bord:
				h += i.count(0)
			if not sum([i.count(0) for i in bord]):
				return "tie"
			return False

		def get_empty_ttt(self, board):
			lst = []
			for x, row in enumerate(board):
				for y, column in enumerate(row):
					if not column:
						lst.append((str(x),str(y)))
			return lst


	class TicTacToeButtons(commands.Cog):
		def __init__(self, bot):
			self.bot = bot

		@commands.command(aliases=['ttt'])
		async def tictactoe(self, ctx, member:discord.Member=None):
			member = member or self.bot.user
			await ctx.send('Tic Tac Toe: X goes first', view=TicTacToe(ctx, [ctx.author,member]))
except AttributeError:
	class TicTacToeButtons:
		pass