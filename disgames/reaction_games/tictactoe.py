import discord

from .. import FormatType

try:
	import format_game
	better_formatting = True
except ImportError:
	better_formatting = False


class TicTacToe:
	def __init__(self, ctx, *, x, o, controls=None, format_type=FormatType.emojis, format_dict={}):

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
		self.format_type = format_type

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

			if self.format_type in [FormatType.emojis, FormatType.emojis_codeblock]:
				format_dict = {k:self.format_dict.get(k, v) for k, v in list(self.default_format_dict.items())}
				format_dict.update({1:'1️⃣',2:'2️⃣',3:'3️⃣','a':':regional_indicator_a:','b':':regional_indicator_b:','c':':regional_indicator_c:'})
				return format_game.format_tictactoe_board(self.board, filler_char="⏹", replacements=format_dict, codeblock=self.format_type == FormatType.emojis_codeblock, mixed_coordinates=True)

			is_listed = self.format_type in [FormatType.listed, FormatType.listed_codeblock]
			filler_char = '    ' if is_listed else ' '

			return format_game.format_tictactoe_board(self.board, codeblock=self.format_type in [FormatType.plain_codeblock, FormatType.listed_codeblock], mixed_coordinates=True, filler_char = filler_char, vertical_join=' | ' if is_listed else '', horizontal_join='\n  +---+---+---+' if is_listed else '', join_upper_coordinates='   ' if is_listed else '')
		else:
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

	async def handle_embed(self, embed_color, send_or_edit='edit', content=''):
		formatted_board = self.format_board()
		if self.format_type != FormatType.image:
			embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}\n{formatted_board}", color=embed_color)

			if send_or_edit == 'send':
				self.msg = await self.ctx.send(content=content, embed=embed)
			else:
				await self.msg.edit(content=content, embed=embed)
		else:
			embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}", color=embed_color)
			embed.set_image(url="attachment://TicTacToe.png")

			if send_or_edit == 'send':
				self.msg = await self.ctx.send(content=content, embed=embed, file=formatted_board)
			else:
				await self.msg.edit(content=content, embed=embed, attachments=[formatted_board])

	async def start(self, *, remove_reaction=False):
		# embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}\n{self.format_board()}", color=ongoing_game_color)
		# self.msg = await self.ctx.send(embed=embed)
		await self.handle_embed(ongoing_game_color, 'send')
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
				await self.handle_embed(lost_game_color, 'edit', f"Game ended by: {u.mention}")
				# embed = discord.Embed(title='Tic Tac Toe', description=f"Game ended by: {u.mention}\n{self.format_board()}", color=lost_game_color)
				# await self.msg.edit(content=f'Game ended!', embed=embed)
				self.winner = self.x if u == self.o else self.o
				break

			if u == self.turn:
				x,y = inp
				self.board[x][y] = self.conversion[self.turn]
				won = self.has_won()
				if won == True:
					# embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}\n{self.format_board()}", color=won_game_color)
					# await self.msg.edit(content=f'{self.turn.mention} won!', embed=embed)
					await self.handle_embed(won_game_color, 'edit', f'{self.turn.mention} won!')
					self.winner = self.turn
					break
				elif won == False:
					# embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}\n{self.format_board()}", color=drawn_game_color)
					# await self.msg.edit(content=f'Draw', embed=embed)
					await self.handle_embed(drawn_game_color, 'edit', f'Draw')
					self.winner = None
					break
				else:
					self.turn = self.x if self.turn == self.o else self.o
					# embed = discord.Embed(title='Tic Tac Toe', description=f"Turn: {self.turn.mention}\n{self.format_board()}", color=ongoing_game_color)
					# await self.msg.edit(embed=embed)
					await self.handle_embed(ongoing_game_color, 'edit')
				self.controls.pop(r.emoji)
		return self.winner
