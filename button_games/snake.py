import random
import copy
import discord
import asyncio
from discord.ext import commands, tasks

class SnakeGame:
	def __init__(self, board):
		self.length = 1
		self.snake =  [[len(board)//2,len(board[0])//2]]
		self.direction = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
		self.board = board
		self.make_apple()

	def has_won_snake(self):
		return self.length == 100

	def get_head_position(self):
		return self.snake[0]

	def point(self, pt):
		if self.length > 1 and (pt[0] * -1, pt[1] * -1) == self.direction:
			pass
		else:
			self.direction = pt

	def move(self):
		cur = self.snake[0]
		x, y = self.direction
		new = [cur[0]+x, cur[1]+y]
		if len(self.snake) > 2 and new in self.snake[2:]:
			return True
		if new[0] >= len(self.board):
			new[0] = 0
		elif new[0] == -1:
			new[0] = len(self.board)-1
		if new[1] >= len(self.board[0]):
			new[1] = 0
		elif new[1] == -1:
			new[1] = len(self.board[0])-1
		if tuple(new) == self.apple:
			self.board[self.apple[0]][self.apple[1]] = ' '
			self.make_apple()
			self.length += 1
		self.snake.insert(0, new)
		if len(self.snake) > self.length:
			self.snake.pop()

	def get_board(self):
		board = copy.deepcopy(self.board)
		for row in self.snake:
			board[row[0]][row[1]] = 'b'
		return board

	def make_apple(self):
		x = random.randint(0, len(self.board)-1)
		y = random.randint(0, len(self.board[0])-1)
		while [x,y] in self.snake:
			x = random.randint(0, len(self.board)-1)
			y = random.randint(0, len(self.board[0])-1)
		self.board[x][y] = 'a'
		self.apple = x, y

class SnakeButton(discord.ui.Button):
	def __init__(self, emoji, row):
		super().__init__(emoji=emoji, row=row, label='\u200b', disabled=not bool(emoji))
		if bool(emoji):
			self.style = discord.ButtonStyle.blurple

	async def callback(self, interaction):
		await interaction.response.defer()
		view = self.view

		inp = view.controls[str(self.emoji)]
		view.snake_game.point(inp)

class Snake(discord.ui.View):
	def __init__(self, ctx, *, format_dict={}, board_size=10):
		super().__init__()

		from .. import resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color
		global resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color

		self.ctx = ctx
		self.board = [[' ' for _ in range(board_size)] for _ in range(board_size)]
		self.format_dict = format_dict

		UP    = (-1, 0)
		DOWN  = (1, 0)
		LEFT  = (0, -1)
		RIGHT = (0, 1)

		self.controls = {'⬆':UP, '⬇':DOWN, '⬅':LEFT, '➡':RIGHT}

		self.msg = None
		self.winner = 0

		self.add_item(SnakeButton(None,1))
		self.add_item(SnakeButton('⬆',1))
		self.add_item(SnakeButton(None,1))
		self.add_item(SnakeButton('⬅',2))
		self.add_item(SnakeButton('🔄',2))
		self.add_item(SnakeButton('➡',2))
		self.add_item(SnakeButton(None,3))
		self.add_item(SnakeButton('⬇',3))
		self.add_item(SnakeButton(None,3))

	async def interaction_check(self, interaction):
		if interaction.user != self.ctx.author:
			return await interaction.response.send_message(content='This is not your game', ephemeral=True)

	def format_board(self, board, snake_head):
		lst = []
		dct = {'a':'🍎', 'h':'😳', 'b':'🟡', ' ':'⬛'}
		for x, row in enumerate(board):
			lst.append(''.join([(self.format_dict.get('h', dct.get('h')) if [x,y] == snake_head else self.format_dict.get(col, dct.get(col))) for y, col in enumerate(row)]))
		return '\n'.join(lst)

	async def end_game(self, interaction):
		self.winner = False
		self.stop()
		for child in self.children:
			child.disabled = True
		embed = discord.Embed(title='Snake', description=self.format_board(self.snake_game.get_board(), self.snake_game.get_head_position()), color=lost_game_color)
		await interaction.response.edit_message(content="You lost", embed=embed, view=self)
		self.run = False

	async def snake_loop(self):
		while self.run:
			lost = self.snake_game.move()
			embed = discord.Embed(title='Snake', description=self.format_board(self.snake_game.get_board(), self.snake_game.get_head_position()), color=ongoing_game_color)
			if lost:
				embed.color = lost_game_color
				await self.msg.edit(content='You lost', embed=embed)
				self.run = False
				self.winner = False
				self.stop()
				return

			if self.snake_game.has_won_snake():
				embed.color = won_game_color
				await self.msg.edit(content='You won', embed=embed)
				self.run = False
				self.winner = True
				self.stop()
				return

			await self.msg.edit(embed=embed)
			await asyncio.sleep(1.5)


	async def start(self, *, end_game_option=False):
		self.snake_game = SnakeGame(self.board)

		if end_game_option:
			button = discord.ui.Button(emoji='⏹', style=discord.ButtonStyle.danger, row=4)
			button.callback = self.end_game
			self.add_item(button)

		embed = discord.Embed(title='Snake', description=self.format_board(self.snake_game.get_board(), self.snake_game.get_head_position()), color=ongoing_game_color)
		self.msg = await self.ctx.send(embed=embed, view=self)

		self.run = True
		self.ctx.bot.loop.create_task(self.snake_loop())

		await self.wait()
		return self.winner