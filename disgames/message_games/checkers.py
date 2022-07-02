import discord

class Checkers:
	def __init__(self, ctx, *, red, blue, format_dict={}):

		from .. import resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color
		global resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color

		self.ctx = ctx
		self.format_dict = format_dict
		self.board = [
			[" ", "b", " ", "b", " ", "b", " ", "b"],
			["b", " ", "b", " ", "b", " ", "b", " "],
			[" ", "b", " ", "b", " ", "b", " ", "b"],
			[" ", " ", " ", " ", " ", " ", " ", " "],
			[" ", " ", " ", " ", " ", " ", " ", " "],
			["r", " ", "r", " ", "r", " ", "r", " "],
			[" ", "r", " ", "r", " ", "r", " ", "r"],
			["r", " ", "r", " ", "r", " ", "r", " "],
		]
		self.opts = {"ul": (-1,-1), "ur": (-1,1), "dl": (1,-1), "dr": (1,1)}
		self.turn = 'r'
		self.other_turn = 'b'
		self.turns = {'r':red,'b':blue}
		self.colors = {'r':'Red','b':'Blue'}

	def format_board(self):
		lst = [':stop_button::regional_indicator_a::regional_indicator_b::regional_indicator_c::regional_indicator_d::regional_indicator_e::regional_indicator_f::regional_indicator_g::regional_indicator_h:']
		dct = {"r": "🔴", "b": "🔵", " ": "⬛", "rk": "♦", "bk": "🔷"}
		for i in range(1, 10):
			dct[i] = f"{i}\N{variation selector-16}\N{combining enclosing keycap}"

		for num, row in enumerate(self.board):
			lst.append(dct[num+1]+''.join([self.format_dict.get(i, dct.get(i, i)) for i in row]))
		return '\n'.join(lst)

	def has_won(self):
		nos = {" ": 0, "r": 0, "b": 0}
		for row in self.board:
			for col in row:
				nos[col[0]] += 1

		if nos["b"] == 0:
			return "r"
		elif nos["r"] == 0:
			return "b"

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

		if (not x in range(10)) or (not y in range(10)):
			return None
		return x, y

	def convert_to_coors(self, x, y):
		x = str(x+1)
		y = chr(y+ord('a'))
		return x+y

	def valid_moves(self, x, y):
		moves = []
		dirs = None
		try:
			dirs = {'r':['ul','ur'],'b':['dl','dr']}[self.board[x][y]]
		except KeyError:
			dirs = ['ul','ur','dl','dr']
		xy = self.convert_to_coors(x, y)
		for i in dirs:
			inc = self.opts[i]
			x_ = x+inc[0]
			y_ = y+inc[1]
			x__ =  x+(inc[0]*2)
			y__ =  y+(inc[1]*2)
			if(x > 7 or x < 0):
				continue
			elif y > 7 or y < 0:
				continue
			elif x_ > 7 or x_ < 0:
				continue
			elif y_ > 7 or y_ < 0:
				continue
			else:
				try:
					if self.board[x_][y_] == ' ':
						moves.append(f"{i} {xy}")
					elif self.board[x_][y_][0] == self.other_turn:
						if self.board[x__][y__] == ' ':
							if x__ > 7 or x__ < 0:
								continue
							elif y__ > 7 or y__ < 0:
								continue
							moves.append(f"{i} {xy}")
				except IndexError:
					pass
		return moves

	def moves(self):
		r_moves = []
		b_moves = []
		for x in range(len(self.board)):
			for y in range(len(self.board[x])):
				if self.board[x][y] != ' ':
					moves = self.valid_moves(x, y)
					if self.board[x][y][0] == 'r':
						r_moves.extend(moves)
					else:
						b_moves.extend(moves)
		return {'r':r_moves,'b':b_moves}[self.turn]

	def format_moves(self):
		moves = self.moves()
		string = ''
		for move in moves:
			string += '`'+move+'`, '
		return string[:-2]

	async def start(self, *, delete_input=False, end_game_option=False, resend_embed_option=False):

		embed = discord.Embed(title='Checkers', description=f"Turn: {self.turns[self.turn].mention} ({self.colors[self.turn]})\n{self.format_board()}", color=ongoing_game_color)
		embed.add_field(name='Moves:', value=self.format_moves())

		self.msg = await self.ctx.send(embed=embed)

		while True:
			inp = await self.ctx.bot.wait_for('message', check=lambda m: m.author in list(self.turns.values()) and m.channel == self.ctx.channel)

			if delete_input:
				try:
					await inp.delete()
				except discord.Forbidden:
					pass

			if end_game_option and inp.content.lower() in end_game_list:
				embed = discord.Embed(title='Checkers', description=f"Turn: {self.turns[self.turn].mention} ({self.colors[self.turn]})\n{self.format_board()}", color=lost_game_color)
				await self.msg.edit(content='Game ended', embed=embed)
				break
			elif resend_embed_option and inp.content.lower() in resend_embed_list:
				embed = discord.Embed(title='Checkers', description=f"Turn: {self.turns[self.turn].mention} ({self.colors[self.turn]})\n{self.format_board()}", color=ongoing_game_color)
				embed.add_field(name='Moves:', value=self.format_moves())
				self.msg = await self.ctx.send(embed=embed)

			if inp.author == self.turns[self.turn]:
				try:
					direction = inp.content.lower().split(' ')[0]
					xy = inp.content.lower().split(' ')[1]
				except IndexError:
					continue
				xy = self.get_coors(xy)
				if not xy:
					continue
				x, y = xy

				moves = self.moves()
				if direction+' '+self.convert_to_coors(x, y) in moves:
					opt = self.opts[direction]
					self.board[x][y] = ' '
					if self.board[x+opt[0]][y+opt[1]] != ' ':
						turn = self.turn
						if x+(opt[0]*2) == 7 or x+(opt[0]*2) == 0:
							turn = 'k'+turn
						self.board[x+(opt[0]*2)][y+(opt[1]*2)] = turn
					else:
						turn = self.turn
						if x+opt[0] == 7 or x+opt[0] == 0:
							turn = 'k'+turn
						self.board[x+opt[0]][y+opt[1]] = turn
					won = self.has_won()
					if won:
						embed = discord.Embed(title='Checkers', description=f"Winner: {self.turns[self.turn].mention} ({self.colors[self.turn]})\n{self.format_board()}", color=won_game_color)
						embed.add_field(name='Moves:', value='No legal moves')
						await self.msg.edit(content='You won!', embed=embed)
						break
					else:
						self.turn = self.other_turn
						self.other_turn = 'r' if self.other_turn == 'b' else 'b'
						embed = discord.Embed(title='Checkers', description=f"Turn: {self.turns[self.turn].mention} ({self.colors[self.turn]})\n{self.format_board()}", color=ongoing_game_color)
						embed.add_field(name='Moves:', value=self.format_moves())
						await self.msg.edit(embed=embed)