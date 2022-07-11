import discord
from .. import FormatType

try:
	import format_game
	better_formatting = True
except ImportError:
	better_formatting = False

class TicTacToe:
	def __init__(self, ctx, *, format_type=FormatType.emojis, x, o, format_dict={}):

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
		self.format_type = format_type
		self.winner = 0

	def format_board(self):
		if better_formatting:
			if self.format_type == FormatType.image:
				import io

				arr = io.BytesIO()
				im = format_game.format_tictactoe_board(self.board, image=True, mixed_coordinates=True)
				im.save(arr, format='PNG')
				arr.seek(0)
				file = discord.File(arr, filename='TicTacToe.png')
				return file
			
			if self.format_type in [FormatType.emoji, FormatType.emoji_codeblock]:
				format_dict = {k:self.format_dict.get(k, v) for k, v in self.default_format_dict}
				format_dict.update({1:'1️⃣',2:'2️⃣',3:'3️⃣','a':':regional_indicator_a:','b':':regional_indicator_b:','c':':regional_indicator_c:'})
				return format_game.format_tictactoe_board(self.board, filler_char="⏹", replacements=format_dict, codeblock=self.format_type == FormatType.emoji_codeblock)

			is_listed =  self.format_type in [FormatType.listed, FormatType.listed_codeblock]
			filler_char = '    ' if is_listed else ''

			return format_game.format_tictactoe_board(self.board, codeblock=self.format_type in [FormatType.plain_codeblock, FormatType.listed_codeblock], mixed_coordinates=True, filler_char = filler_char, vertical_join=' | ' if is_listed else '', horizontal_join='\n  +---+---+---+' if is_listed else '', join_upper_coordinates='   ' if is_listed else '')
		else:
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
		formatted_board = self.format_board()
		if self.format_type != FormatType.image:
			embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}\n{formatted_board}", color=ongoing_game_color)
			self.msg = await self.ctx.send(embed=embed)
		else:
			embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}", color=ongoing_game_color)
			embed.set_image(url="attachment://TicTacToe.png")
			self.msg = await self.ctx.send(embed=embed, file=formatted_board)
		while True:
			msg = await self.ctx.bot.wait_for('message', check=lambda m:m.author==self.turn and m.channel==self.ctx.channel)

			if delete_input:
				try:
					await msg.delete()
				except discord.Forbidden:
					pass

			if resend_embed_option and msg.content.lower() in resend_embed_list:
				formatted_board = self.format_board()
				if self.format_type != FormatType.image:
					embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}\n{formatted_board}", color=ongoing_game_color)
					self.msg = await self.ctx.send(embed=embed)
				else:
					embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}", color=ongoing_game_color)
					embed.set_image(url="attachment://TicTacToe.png")
					self.msg = await self.ctx.send(embed=embed, file=formatted_board)				
					continue

			elif msg.content.lower() in end_game_list:
				embed = self.msg.embeds[0]
				embed.color = lost_game_color
				# embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}\n{self.format_board()}", color=lost_game_color)
				await self.msg.edit(content=f'Game ended!', embed=embed)
				self.winner = self.x if msg.author == self.o else self.o
				break

			coors = self.get_coors(msg.content)
			if coors and self.board[coors[0]][coors[1]] == ' ':
				x,y = coors
				self.board[x][y] = self.conversion[self.turn]
				won = self.has_won()
				if won == True:

					formatted_board = self.format_board()
					if self.format_type != FormatType.image:
						embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}\n{formatted_board}", color=won_game_color)
						await self.msg.edit(content=f'{self.turn.mention} won!', embed=embed)
					else:
						embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}", color=won_game_color)
						embed.set_image(url="attachment://TicTacToe.png")
						await self.msg.edit(content=f'{self.turn.mention} won!', embed=embed, attachments=[formatted_board])

					# embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}\n{self.format_board()}", color=won_game_color)
					# await self.msg.edit(content=f'{self.turn.mention} won!', embed=embed)
					self.winner = self.turn
					break
				elif won == False:
					formatted_board = self.format_board()
					if self.format_type != FormatType.image:
						embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}\n{formatted_board}", color=drawn_game_color)
						await self.msg.edit(content='Draw', embed=embed)
					else:
						embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}", color=drawn_game_color)
						embed.set_image(url="attachment://TicTacToe.png")
						await self.msg.edit(content='Draw', embed=embed, attachments=[formatted_board])
					self.winner = None
					break
				else:
					self.turn = self.x if self.turn == self.o else self.o
					formatted_board = self.format_board()
					if self.format_type != FormatType.image:
						embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}\n{formatted_board}", color=ongoing_game_color)
						await self.msg.edit(embed=embed)
					else:
						embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}", color=ongoing_game_color)
						embed.set_image(url="attachment://TicTacToe.png")
						await self.msg.edit(embed=embed, attachments=[formatted_board])
		return self.winner