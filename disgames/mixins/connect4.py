import discord, random
from discord.ext import commands

class Connect4(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def format_board(self, board):
		toDisplay = ""
		dct = {'b':'🔵','r':'🔴',' ':'⬛','R':'♦️','B':'🔷'}
		for y in range(6):
			for x in range(6):
				toDisplay+=dct[board[y][x]]
			toDisplay+=board[y][6] + '\n'
		return toDisplay

	def has_won(self, height, width, board):
		for y in range(height):
			for x in range(width-3):
				if(board[y][x]==board[y][x+1] and board[y][x]==board[y][x+2] and board[y][x]==board[y][x+3] and board[y][x]!=' '):
					if(board[y][x]=='b'):
						board[y][x] = 'B'
						board[y][x+1] = 'B'
						board[y][x+2] = 'B'
						board[y][x+3] = 'B'
					elif(board[y][x]=='r'):
						board[y][x]="R"
						board[y][x+1]="R"
						board[y][x+2]="R"
						board[y][x+3]="R"
					return True, board, "in a horizontal row"
		for y in range(height-3):
			for x in range(width):
				if(board[y][x]==board[y+1][x] and board[y][x]==board[y+2][x] and board[y][x]==board[y+3][x] and board[y][x]!=' '):
					if(board[y][x]=='b'):
						board[y][x] = 'B'
						board[y+1][x] = 'B'
						board[y+2][x] = 'B'
						board[y+3][x] = 'B'
					elif(board[y][x]=='r'):
						board[y][x]="R"
						board[y+1][x]="R"
						board[y+2][x]="R"
						board[y+3][x]="R"
					return True, board, "in a Vertical row"
		for y in range(height-3):
			for x in range(width-3):
				if(board[y][x]==board[y+1][x+1] and board[y][x]==board[y+2][x+2] and board[y][x]==board[y+3][x+3] and board[y][x]!=' '):
					if(board[y][x]=='b'):
						board[y][x] = 'B'
						board[y+1][x+1] = 'B'
						board[y+2][x+2] = 'B'
						board[y+3][x+3] = 'B'
					elif(board[y][x]=='r'):
						board[y][x]="R"
						board[y+1][x+1]="R"
						board[y+2][x+2]="R"
						board[y+3][x+3]="R"
					return True, board, "on a \ diagonal"
		for y in range(height-3):
			for x in range(3,width):
				if(board[y][x]==board[y+1][x-1] and board[y][x]==board[y+2][x-2] and board[y][x]==board[y+3][x-3] and board[y][x]!=' '):
					if(board[y][x]=='b'):
						board[y][x] = 'B'
						board[y+1][x-1] = 'B'
						board[y+2][x-2] = 'B'
						board[y+3][x-3] = 'B'
					elif(board[y][x]=='r'):
						board[y][x]="R"
						board[y+1][x-1]="R"
						board[y+2][x-2]="R"
						board[y+3][x-3]="R"
					return True, board, "in a / diagonal"
		return None, None, None

	@commands.command()
	async def connect4(self, ctx, member:discord.Member=None):
		if member is None:
			board = [[' ' for _ in range(7)] for i in range(6)]
			e = discord.Embed(title='Connect4', description=self.format_board(board), color=discord.Color.blurple())
			msg = await ctx.send(embed=e)
			turn = ctx.author
			while True:
				e = discord.Embed(title='Connect4', description=self.format_board(board), color=discord.Color.blurple())
				await msg.edit(embed=e)
				if turn == ctx.author:
					inp = await self.bot.wait_for('message', check = lambda m:m.author == turn and m.channel == ctx.channel and len(m.content)==1)
					try:
						x = int(inp.content)-1
					except ValueError:
						await ctx.send(f"Invalid Syntax: {inp.content} is not a number")
						continue
					if x > 6 or x < 0:
						await ctx.send(f"Invalid syntax: {inp.content} isnt a valid place on the board")
						continue
					y = 0
					while y <= 6:
						if y == 6:
							await ctx.send("Invalid Syntax: Cant add to this column anymore")
							break
						if board[5-y][x] == ' ':
							board[5-y][x] = 'r' if turn == ctx.author else 'b'
							break	
						else:
							y += 1
				else:
					x = random.randint(0,6)
					h = True
					while h:
						y = 0
						while y <= 6:
							if y == 6:
								x = random.randint(0,6)
								break
							if board[5-y][x] == ' ':
								board[5-y][x] = 'r' if turn == ctx.author else 'b'
								h = False
								break
							else:
								y += 1

				won = self.has_won(6, 7, board)
				if won[0]:
					await ctx.send(f'{turn.mention} connected 4 {won[2]}')
					e = discord.Embed(title='Connect4', description=self.format_board(won[1]), color=discord.Color.blurple())
					await ctx.send(embed=e)
					return
				turn = bot.user if turn == ctx.author else ctx.author
		elif member.bot or member == ctx.author:
			return await ctx.send(f"Invalid Syntax: Can't play against {member.display_name}")
		else:
			board = [[' ' for _ in range(7)] for i in range(6)]
			e = discord.Embed(title='Connect4', description=self.format_board(board), color=discord.Color.blurple())
			msg = await ctx.send(embed=e)
			turn = ctx.author
			while True:
				e = discord.Embed(title='Connect4', description=self.format_board(board), color=discord.Color.blurple())
				await msg.edit(embed=e)
				inp = await self.bot.wait_for('message', check = lambda m:m.author == turn and m.channel == ctx.channel and len(m.content)==1)
				try:
					x = int(inp.content)-1
				except ValueError:
					await ctx.send(f"Invalid Syntax: {inp.content} is not a number")
					continue
				if x > 6:
					await ctx.send(f"Invalid syntax: {inp.content} isnt a valid place on the board")
					continue
				y = 0
				while y <= 6:
					if y == 6:
						await ctx.send("Invalid Syntax: Cant add to this column anymore")
						break
					if board[5-y][x] == ' ':
						board[5-y][x] = 'r' if turn == ctx.author else 'b'
						break	
					else:
						y += 1
				won = self.has_won(6, 7, board)
				if won[0]:
					await ctx.send(f'{turn.mention} connected 4 {won[2]}')
					e = discord.Embed(title='Connect4', description=self.format_board(won[1]), color=discord.Color.blurple())
					await ctx.send(embed=e)
					return
				turn = member if turn == ctx.author else ctx.author