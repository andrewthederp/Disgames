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

class Snake:
	def __init__(self, ctx, *, format_dict={}, board_size=10):

		from .. import resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color
		global resend_embed_list, end_game_list, ongoing_game_color, lost_game_color, won_game_color

		self.ctx = ctx
		self.board = [[' ' for _ in range(board_size)] for _ in range(board_size)]
		self.format_dict = format_dict

		UP    = (-1, 0)
		DOWN  = (1, 0)
		LEFT  = (0, -1)
		RIGHT = (0, 1)

		self.conversion = {'u':UP, 'd':DOWN, 'l':LEFT, 'r':RIGHT}

		self.msg = None

	def format_board(self, board, snake_head):
		lst = []
		dct = {'a':'🍎', 'h':'😳', 'b':'🟡', ' ':'⬛'}
		for x, row in enumerate(board):
			lst.append(''.join([(self.format_dict.get('h', dct.get('h')) if [x,y] == snake_head else self.format_dict.get(col, dct.get(col))) for y, col in enumerate(row)]))
		return '\n'.join(lst)

	async def snake_loop(self):
		while self.run:
			lost = self.snake_game.move()
			embed = discord.Embed(title='Snake', description=self.format_board(self.snake_game.get_board(), self.snake_game.get_head_position()), color=ongoing_game_color)
			if lost:
				embed.color = lost_game_color
				await self.msg.edit(content='You lost', embed=embed)
				self.run = False
				self.winner = False
				return

			if self.snake_game.has_won_snake():
				embed.color = won_game_color
				await self.msg.edit(content='you won!!!', embed=embed)
				self.run = False
				self.winner = True
				return

			await self.msg.edit(embed=embed)
			await asyncio.sleep(1.5)


	async def start(self, *, delete_input=False, end_game_option=False, resend_embed_option=False):
		self.snake_game = SnakeGame(self.board)

		embed = discord.Embed(title='Snake', description=self.format_board(self.snake_game.get_board(), self.snake_game.get_head_position()), color=ongoing_game_color)
		self.msg = await self.ctx.send(embed=embed)

		control_lst = ['u','d','l','r','up','left','right','down']
		if end_game_option:
			control_lst.extend(end_game_list)
		if resend_embed_list:
			control_lst.extend(resend_embed_list)

		self.run = True
		self.ctx.bot.loop.create_task(self.snake_loop())

		def check(m):
			return m.author == self.ctx.author and m.channel == self.ctx.channel and m.content.lower() in control_lst

		while self.run:
			inp = await self.ctx.bot.wait_for('message', check=check)

			if delete_input:
				try:
					await inp.delete_input()
				except discord.Forbidden:
					pass

			if inp.content.lower() in end_game_list:
				embed = discord.Embed(title='Snake', description=self.format_board(self.snake_game.get_board(), self.snake_game.get_head_position()), color=lost_game_color)
				await self.inp.edit(content="You lost", embed=embed)
				self.run = False
				break
			elif inp.content.lower() in resend_embed_list:
				embed = discord.Embed(title='Snake', description=self.format_board(self.snake_game.get_board(), self.snake_game.get_head_position()), color=ongoing_game_color)
				self.inp = await self.ctx.send(embed=embed)
				continue
			self.snake_game.point(self.conversion[inp.content.lower()[0]])
		return self.winner