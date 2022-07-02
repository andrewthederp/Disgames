import discord
import random
import copy

class Sokoban:
	def __init__(self, ctx, *, play_forever=False, format_dict={}, board=None):

		from .. import ongoing_game_color, lost_game_color, won_game_color
		global ongoing_game_color, lost_game_color, won_game_color

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
				elif item=='w':
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
		self.won = True
		return True


	async def start(self, *, remove_reaction=False):
		embed = discord.Embed(title='Sokoban', description=self.format_board(), color=ongoing_game_color)
		self.msg = await self.ctx.send(embed=embed)
		for reaction in self.converesion.keys():
			await self.msg.add_reaction(reaction)

		while True:
			r,u = await self.ctx.bot.wait_for('reaction_add', check=lambda r,u: u == self.ctx.author and r.message == self.msg and str(r) in list(self.converesion.keys()))

			if remove_reaction:
				try:
					await r.message.remove_reaction(r.emoji,u)
				except discord.Fobidden:
					pass

			inp = self.converesion[r.emoji]

			try:

				if inp == 'reload':
					self.board = self.original_board
					self.original_board = copy.deepcopy(self.board)
				
				direction = self.controls[inp]
				self.move(direction, 1)
				if self.has_won():
					if self.play_forever:
						self.board = self.create_board()
						self.original_board = copy.deepcopy(self.board)
						self.won = False
					else:
						embed = discord.Embed(title='Sokoban', description=self.format_board(), color=won_game_color)
						await self.msg.edit(content='You won!', embed=embed)
						break

			except KeyError:
				if inp == 'stop':
					self.won = False
					embed = discord.Embed(title='Sokoban', description=self.format_board(), color=lost_game_color)
					await self.msg.edit(content='Game ended!', embed=embed)
					break
			embed = discord.Embed(title='Sokoban', description=self.format_board(), color=ongoing_game_color)
			await self.msg.edit(embed=embed)
		return self.won