import random
import copy
import time
import os
import discord
from discord.ext import commands
import asyncio

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
		if self.length <= 1 or (pt[0] * -1, pt[1] * -1) != self.direction:
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
			board[row[0]][row[1]] = 's'
		return board

	def make_apple(self):
		x = random.randint(0, len(self.board)-1)
		y = random.randint(0, len(self.board[0])-1)
		while [x,y] in self.snake:
			x = random.randint(0, len(self.board)-1)
			y = random.randint(0, len(self.board[0])-1)
		self.board[x][y] = 'a'
		self.apple = x, y

class Snake(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def format_board(self, board, snake_head):
		lst = []
		dct = {'a':'🍎', 'S':'😳', 's':'🟡', ' ':'⬛'}
		for x, row in enumerate(board):
			scn_lst = []
			for y, column in enumerate(row):
				if [x,y] == snake_head:
					scn_lst.append(dct["S"])
				else:
					scn_lst.append(dct[column])
			lst.append(''.join(scn_lst))
		return '\n'.join(lst)

	@commands.command()
	async def snake(self, ctx):
		board = [[' ' for _ in range(10)] for _ in range(10)]
		UP    = (-1, 0)
		DOWN  = (1, 0)
		LEFT  = (0, -1)
		RIGHT = (0, 1)
		conversion = {'⬅':LEFT, '⬆':UP, '➡':RIGHT, '⬇':DOWN}
		s = SnakeGame(board)
		embed = discord.Embed(title='Snake', description=self.format_board(s.get_board(), s.get_head_position()), color=discord.Color.blurple())
		msg = await ctx.send(embed=embed)
		emojis = ['⬅','⬆','➡','⬇']
		for emoji in emojis:
			await msg.add_reaction(emoji)
		while True:
			await msg.edit(embed=discord.Embed(title='Snake', description=self.format_board(s.get_board(), s.get_head_position()), color=discord.Color.blurple()))
			try:
				reaction, _ = await self.bot.wait_for('reaction_add', check = lambda r, u: u == ctx.author and str(r) in emojis and r.message == msg, timeout=1.5)
			except asyncio.TimeoutError:
				lost = s.move()
			else:
				try:
					await msg.remove_reaction(str(reaction), ctx.author)
				except discord.Forbidden:
					pass
				s.point(conversion[str(reaction)])
				lost = s.move()
			if lost:
				await ctx.send('Your snake bit itself :pensive:')
				break
			if s.has_won_snake():
				await ctx.send('you won!!!')
				break
