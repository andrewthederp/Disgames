import discord
import chess
import datetime
import chess.pgn
import itertools

from .. import FormatType
try:
	import format_game
	better_formatting = True
except ImportError:
	better_formatting = False


class Chess:
	def __init__(self, ctx, *, white, black, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR', chess960=None, format_type=FormatType.image, theme='green'):

		from .. import resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color, drawn_game_color
		global resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color, drawn_game_color

		self.ctx = ctx
		self.white = white
		self.black = black
		self.turn = 'w'
		self.turns = {'w':white,'b':black}
		self.colors = {'w':'White','b':"Black"}
		self.status = None

		self.winner = 0

		self.board = chess.Board(fen)

		self.format_type = format_type
		self.theme = theme

		if chess960:
			self.board.set_chess960_pos(chess960)
		else:
			self.board.castling_rights |= chess.BB_H1
			self.board.castling_rights |= chess.BB_A1
			self.board.castling_rights |= chess.BB_H8
			self.board.castling_rights |= chess.BB_A8

		now = datetime.datetime.utcnow()
		self.game = chess.pgn.Game(
			headers={
				'Site':'discord.com',
				'Date':f'{now:%Y-%m-%d}',
				'White':white.display_name,
				'Black':black.display_name, 
			}
		)
		self.game.setup(self.board)
		self.node = self.game

	async def has_won(self):
		value = None
		result = self.board.result()

		if self.board.is_game_over():
			self.game.headers["Result"] = result

		if self.board.is_checkmate():
			value = f"Checkmate, Winner: {self.turns[self.turn]} | Score: `{result}`"
			self.status = 'win'
		elif self.board.is_stalemate():
			value = f"Stalemate | Score: `{result}`"
			self.status = 'draw'
		elif self.board.is_insufficient_material():
			value = f"Insufficient material left to continue the game | Score: `{result}`"
			self.status = 'draw'
		elif self.board.is_seventyfive_moves():
			value = f"75-moves rule | Score: `{result}`"
			self.status = 'draw'
		elif self.board.is_fivefold_repetition():
			value = f"Five-fold repitition. | Score: `{result}`"
			self.status = 'draw'
		return value

	def get_past_fen(self):
		try:
			board_copy = self.board.copy()
			board_copy.pop()
			return board_copy.board_fen()
		except IndexError:
			return None

	def format_board(self):
		if better_formatting:
			if self.format_type == FormatType.image:
				import io

				arr = io.BytesIO()
				im = format_game.format_chess_board(self.board.board_fen(), image=True, mixed_coordinates=True, board_theme=self.theme, piece_theme=self.theme, past_fen=self.get_past_fen())
				im.save(arr, format='PNG')
				arr.seek(0)
				file = discord.File(arr, filename='Chess.png')
				return file

			is_listed = self.format_type in [FormatType.listed, FormatType.listed_codeblock]
			return format_game.format_chess_board(self.board.board_fen(), codeblock=self.format_type in [FormatType.plain_codeblock, FormatType.listed_codeblock], mixed_coordinates=True, vertical_join=' | ' if is_listed else '', horizontal_join='+---'*8+'+' if is_listed else '', join_upper_coordinates='   ' if is_listed else '', filler_char='    ' if is_listed else ' ')
		else:
			return f"http://www.fen-to-image.com/image/64/double/coords/{self.board.board_fen()}"

	def make_embed(self):
		won = self.has_won()
		if won:
			self.game.headers["Termination"] = won
		embed = discord.Embed(title='Chess', description=won or f"Turn: {self.turns[self.turn].mention} ({self.colors[self.turn]})", color=ongoing_game_color)
		embed.add_field(name=f"Legal moves", value=", ".join([f"`{str(i)}`" for i in self.board.legal_moves]) or 'No legal moves', inline=False)
		embed.add_field(name="PGN", value=self.game, inline=False)
		return embed

	def handle_embed(self, send_or_edit='edit'):
		embed = self.make_embed()
		formatted_board = self.format_board()

		if self.status == 'win':
			embed.color = won_game_color
			self.winner = self.turns[self.turn]
		elif self.status == 'draw':
			embed.color = drawn_game_color
			self.winner = None
		elif self.winner:
			embed.color = lost_game_color

		if better_formatting and self.format_type in [FormatType.listed, FormatType.listed_codeblock, FormatType.plain, FormatType.plain_codeblock]:
			embed.description += f'\n\n{formatted_board}' 

		if better_formatting and self.format_type == FormatType.image:
			embed.set_image(url='attachment://Chess.png')
		elif better_formatting:
			pass
		else:
			embed.set_image(url=formatted_board)

		if send_or_edit == 'send':
			if better_formatting and self.format_type == FormatType.image:
				self.msg = await self.ctx.send(embed=embed, file=formatted_board)
			else:
				self.msg = await self.ctx.send(embed=embed)
		else:
			if better_formatting and self.format_type == FormatType.image:
				await self.msg.edit(embed=embed, attachments=[formatted_board])
			else:
				await self.msg.edit(embed=embed)

	def convert_to_move(self, inp):
		inp = inp.replace(' ', '')
		move = None
		try:
			move = self.board.parse_san(inp)
		except ValueError:
			if len(inp) in range(4, 6):
				for move_ in itertools.permutations(inp.lower()):
					try:
						move = self.board.parse_uci(''.join(move_))
					except ValueError:
						continue
					else:
						break
		return move

	async def start(self, *, delete_input=False, end_game_option=False, resend_embed_option=False):
		embed = self.make_embed()
		# self.msg = await self.ctx.send(embed=embed)
		await self.handle_embed('send')

		while not self.board.is_game_over():
			inp = await self.ctx.bot.wait_for('message', check= lambda m: m.author in [self.white, self.black] and m.channel == self.ctx.channel)

			if delete_input:
				try:
					await inp.delete()
				except discord.Forbidden:
					pass

			if end_game_option and inp.content.lower() in end_game_list:
				winner = self.white if inp.author == self.black else self.black
				self.winner = winner
				self.game.headers['Result'] = '1-0' if winner == self.white else '0-1'
				self.game.headers["Termination"] = f"{winner.display_name} won by resignation"
				# embed = self.make_embed()
				# embed.color = lost_game_color
				# await self.msg.edit(embed=embed)
				await self.handle_embed('edit')
				break
			elif resend_embed_option and inp.content.lower() in resend_embed_list:
				# embed = self.make_embed()
				# self.msg = await self.ctx.send(embed=embed)
				await self.handle_embed('send')

			if inp.author == self.turns[self.turn]:
				move = self.convert_to_move(inp.content)
				if move:
					self.board.push(move)
					self.node = self.node.add_variation(move)
					# embed = self.make_embed()

					await self.handle_embed(send_or_edit='edit')

					self.turn = 'w' if self.turn == 'b' else 'b'
		return self.winner
