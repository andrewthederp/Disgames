import discord
import random
import copy

class SokobanButton(discord.ui.Button):
	def __init__(self, emoji, row):
		super().__init__(emoji=emoji, row=row, label='\u200b', disabled=not bool(emoji))
		if bool(emoji):
			self.style = discord.ButtonStyle.blurple

	async def callback(self, interaction):
		view = self.view

		inp = view.converesion[self.emoji.name]

		try:
			if inp == 'reload':
				view.board = view.original_board
				view.original_board = copy.deepcopy(view.board)
			
			direction = view.controls[inp]
			view.move(direction, 1)
			if view.has_won():
				if view.play_forever:
					view.board = view.create_board()
					view.original_board = copy.deepcopy(view.board)
				else:
					view.stop()
					view.clear_items()
					embed = discord.Embed(title="Sokoban", description=view.format_board(), color=won_game_color)
					return await interaction.response.edit_message(content='You won!', embed=embed, view=view)
		except KeyError:
			pass
		embed = discord.Embed(title='Sokoban', description=view.format_board(), color=ongoing_game_color)
		await interaction.response.edit_message(embed=embed)


class SokobanView(discord.ui.View):
	def __init__(self, ctx, play_forever=False, format_dict={}, board=None):
		super().__init__()
		self.ctx                 = ctx
		self.board               = board or self.create_board()
		self.controls            = {'u':(-1,0), 'd':(1,0), 'l':(0,-1), 'r':(0,1)}
		self.format_dict         = format_dict
		self.default_format_dict = {
									'p':'😳',
									'tp':'😳',
									't':'❎',
									'b':'🟫',
									'bt':'✅',
									' ':'⬛',
									'w':'⬜'
									}
		self.play_forever        = play_forever
		self.original_board      = copy.deepcopy(self.board)
		self.converesion = {
							'⬆':'u',
							'⬇':'d',
							'⏹':'stop',
							'🔄':'reload',
							'⬅':'l',
							'➡':'r'
							}
		self.winner = []

		self.add_item(SokobanButton(None,1))
		self.add_item(SokobanButton('⬆',1))
		self.add_item(SokobanButton(None,1))
		self.add_item(SokobanButton('⬅',2))
		self.add_item(SokobanButton('🔄',2))
		self.add_item(SokobanButton('➡',2))
		self.add_item(SokobanButton(None,3))
		self.add_item(SokobanButton('⬇',3))
		self.add_item(SokobanButton(None,3))
		# self.add_item(SokobanButton('⏹',4))

	async def interaction_check(self, interaction):
		if self.ctx.author == interaction.user:
			return True
		await interaction.response.send_message(content='This is not your game', ephemeral=True)

	@discord.ui.button(emoji='⏹', row=4, style=discord.ButtonStyle.danger)
	async def end(self, interaction, button):
		self.clear_items()
		embed = discord.Embed(title='Sokoban', description=self.format_board(), color=lost_game_color)
		await interaction.response.edit_message(content='Game ended!', embed=embed, view=self)
		self.winner.append(False)
		self.stop()

	def create_board(self):
		board = [[' ' for _ in range(5)] for _ in range(5)]
		board[random.randrange(len(board))][random.randrange(len(board[0]))] = 'p'

		params = {
			't': (0, len(board)),
			'b':(1, len(board)-1)
		}

		for i in ['t','b','t','b']:
			x = random.randrange(*params[i])
			y = random.randrange(*params[i])
			while board[x][y] != ' ':
				x = random.randrange(*params[i])
				y = random.randrange(*params[i])
			board[x][y] = i
		return board

	def get_player(self):
		for x, row in enumerate(self.board):
			for y, col in enumerate(row):
				if col == 'p' or col == 'tp':
					return x,y


	def move(self, direction, amount):

		x,y = self.get_player()
		if x+(direction[0]*amount) not in range(len(self.board)) or y+(direction[1]*amount) not in range(len(self.board[0])):
			return

		for _ in range(amount):
			p_x,p_y = self.get_player()
			success = True
			board_copy = copy.deepcopy(self.board)
			if (p_x+direction[0] in range(len(board_copy)) and p_y+direction[1] in range(len(board_copy[0]))):

				n_index = (p_x+direction[0],p_y+direction[1])
				item = board_copy[n_index[0]][n_index[1]]
				if item == " ":
					if board_copy[p_x][p_y]=='tp':
						board_copy[p_x][p_y] = 't'
					else:
						board_copy[p_x][p_y] = ' '

					if board_copy[n_index[0]][n_index[1]] == 't':
						board_copy[n_index[0]][n_index[1]] = 'tp'
					else:
						board_copy[n_index[0]][n_index[1]] = 'p'

				elif item[0] == 'b':
					b_direction = (direction[0]*2, direction[1]*2)
					if (p_x+b_direction[0] in range(len(board_copy)) and p_y+b_direction[1] in range(len(board_copy[0]))):
						b_index = [p_x+b_direction[0],p_y+b_direction[1]]
						if board_copy[b_index[0]][b_index[1]] not in ['b','bt','w']:

							if board_copy[p_x][p_y]=='tp':
								board_copy[p_x][p_y] = 't'
							else:
								board_copy[p_x][p_y] = ' '

							if board_copy[n_index[0]][n_index[1]]=='bt':
								board_copy[n_index[0]][n_index[1]] = 'tp'
							elif board_copy[n_index[0]][n_index[1]]=='t':
								board_copy[n_index[0]][n_index[1]] = 'tp'
							else:
								board_copy[n_index[0]][n_index[1]] = 'p'

							if board_copy[b_index[0]][b_index[1]]=='t':
								board_copy[b_index[0]][b_index[1]] = 'bt'
							else:
								board_copy[b_index[0]][b_index[1]] = 'b'
						else:
							success = False
					else:
						success = False

				elif item=='t':
					if board_copy[p_x][p_y]=='tp':
						board_copy[p_x][p_y] = 't'
					else:
						board_copy[p_x][p_y] = ' '
					board_copy[n_index[0]][n_index[1]] = 'tp'
				else:
					success = False
			else:
				success = False

			if success:
				self.board = board_copy


	def format_board(self):
		lst = []
		for row in self.board:
			lst.append(''.join(
				[
					self.format_dict.get(i, self.default_format_dict.get(i,i)) for i in row
				]
			))
		return '\n'.join(lst)

	def has_won(self):
		for row in self.board:
			for col in row:
				if col == 't' or col == 'tp':
					return False
		self.winner.append(True)
		return True

class Sokoban:
	def __init__(self, ctx, *, play_forever=False, format_dict={}, board=None):

		from .. import ongoing_game_color, lost_game_color, won_game_color
		global ongoing_game_color, lost_game_color, won_game_color

		self.ctx          = ctx
		self.board        = board
		self.format_dict  = format_dict
		self.play_forever = play_forever

	async def start(self):
		view = SokobanView(self.ctx, self.play_forever, self.format_dict, self.board)
		embed = discord.Embed(title='Sokoban', description=view.format_board(), color=ongoing_game_color)
		await self.ctx.send(embed=embed, view=view)
		await view.wait()
		return view.winner
