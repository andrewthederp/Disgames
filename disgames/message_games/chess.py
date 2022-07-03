import discord
import chess
import itertools

class Chess:
	def __init__(self, ctx, *, white, black, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR', chess960=None):

		from .. import resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color, drawn_game_color
		global resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color, drawn_game_color

		self.ctx = ctx
		self.white = white
		self.black = black
		self.turn = 'w'
		self.turns = {'w':white,'b':black}
		self.colors = {'w':'White','b':"Black"}
		self.status = None

		self.board = chess.Board(fen)

		if chess960:
			self.board.set_chess960_pos(chess960)
		else:
			self.board.castling_rights |= chess.BB_H1
			self.board.castling_rights |= chess.BB_A1
			self.board.castling_rights |= chess.BB_H8
			self.board.castling_rights |= chess.BB_A8

	def has_won(self):
		value = None
		results = self.board.result()
		if self.board.is_checkmate():
			value = f"Checkmate, Winner: {self.turns[self.turn]} | Score: `{results}`"
			self.status = 'win'
		elif self.board.is_stalemate():
			value = f"Stalemate | Score: `{results}`"
			self.status = 'draw'
		elif self.board.is_insufficient_material():
			value = f"Insufficient material left to continue the game | Score: `{results}`"
			self.status = 'draw'
		elif self.board.is_seventyfive_moves():
			value = f"75-moves rule | Score: `{results}`"
			self.status = 'draw'
		elif self.board.is_fivefold_repetition():
			value = f"Five-fold repitition. | Score: `{results}`"
			self.status = 'draw'
		return value

	def make_embed(self):
		won = self.has_won()
		embed = discord.Embed(title='Chess', description=won or f"Turn: {self.turns[self.turn].mention} ({self.colors[self.turn]})", color=ongoing_game_color)
		url = f"http://www.fen-to-image.com/image/64/double/coords/{self.board.board_fen()}"
		embed.set_image(url=url)
		embed.add_field(name=f"Legal moves", value=", ".join([f"`{str(i)}`" for i in self.board.legal_moves]) or 'No legal moves', inline=False)
		embed.add_field(name="Check", value=self.board.is_check(), inline=False)
		return embed

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
		self.msg = await self.ctx.send(embed=embed)
		while True:
			inp = await self.ctx.bot.wait_for('message', check= lambda m: m.author in [self.white, self.black] and m.channel == self.ctx.channel)
			if delete_input:
				try:
					await inp.delete()
				except discord.Forbidden:
					pass
			if end_game_option and inp.content.lower() in end_game_list:
				embed = self.make_embed()
				embed.color = lost_game_color
				await self.msg.edit(embed=embed)
				self.winner = self.white if inp.author == self.black else self.black
				break
			elif resend_embed_option and inp.content.lower() in resend_embed_list:
				embed = self.make_embed()
				self.msg = await self.ctx.send(embed=embed)

			if inp.author == self.turns[self.turn]:
				move = self.convert_to_move(inp.content)
				if move:
					self.board.push(move)
					embed = self.make_embed()
					if self.status == 'win':
						embed.color = won_game_color
						self.winner = inp.author
					elif self.status == 'draw':
						embed.color = drawn_game_color
						self.winner = None
					await self.msg.edit(embed=embed)

					if self.status:
						break
					self.turn = 'w' if self.turn == 'b' else 'b'
		return self.winner