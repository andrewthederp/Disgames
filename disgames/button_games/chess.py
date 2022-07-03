import discord
import chess
import itertools

class ChessModal(discord.ui.Modal, title='Chess'):
	def __init__(self, button):
		super().__init__()
		self.button = button

	inp = discord.ui.TextInput(
		label='Move',
		placeholder='Type your move here...'
	)

	async def on_submit(self, interaction):
		inp = self.inp.value
		view = self.button.view

		move = view.convert_to_move(inp)

		if move:
			view.board.push(move)
			embed = view.make_embed()
			if view.status == 'win':
				embed.color = won_game_color
				view.winner = interaction.user
			elif view.status == 'draw':
				embed.color = drawn_game_color
				view.winner = None
			await interaction.response.edit_message(embed=embed, view=view)

			if view.status:
				view.stop()
				return
			view.turn = 'w' if view.turn == 'b' else 'b'
		else:
			return await interaction.response.send_message(content='Invalid move', ephemeral=True)

class Chess(discord.ui.View):
	def __init__(self, ctx, *, white, black, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR', chess960=None):
		super().__init__()

		from .. import ongoing_game_color, lost_game_color, won_game_color, drawn_game_color
		global ongoing_game_color, lost_game_color, won_game_color, drawn_game_color

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

	async def interaction_check(self, interaction):
		if interaction.user not in [self.white, self.black]:
			return await interaction.response.send_message(content="You're not playing in this game", ephemeral=True)
		return True

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

	@discord.ui.button(label='move', style=discord.ButtonStyle.blurple)
	async def move(self, interaction, button):
		if not interaction.user == self.turns[self.turn]:
			return await interaction.response.send_message(content="It's not your turn", ephemeral=True)
		await interaction.response.send_modal(ChessModal(button))

	async def end_game(self, interaction):
		self.stop()
		for child in self.children:
			child.disabled = True
		embed = self.make_embed()
		embed.description = f'Game ended by: {interaction.user.mention}'
		embed.color = lost_game_color
		self.winner = self.white if self.black == interaction.user else self.black
		await interaction.response.edit_message(content='Game ended', embed=embed, view=self)

	async def start(self, *, end_game_option=False):
		if end_game_option:
			button = discord.ui.Button(emoji='⏹', style=discord.ButtonStyle.danger)
			button.callback = self.end_game
			self.add_item(button)

		embed = self.make_embed()
		self.msg = await self.ctx.send(embed=embed, view=self)
		await self.wait()
		return self.winner