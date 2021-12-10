import discord
from discord.ext import commands

class Checkers(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def format_checkers_board(self, board):
		dct = {'r':'🔴','b':'🔵',' ':'⬛', 'rk':'♦','bk':'🔷'}
		for i in range(1, 10):
			dct[str(i)] = f"{i}\N{variation selector-16}\N{combining enclosing keycap}"
		lst = ['⏹️'+''.join([dct[str(i+1)] for i in range(len(board[0]))])]
		for x, row in enumerate(board):
			scn_lst = [dct[str(x+1)]]
			for y, column in enumerate(row):
				scn_lst.append(dct[column])
			lst.append(''.join(scn_lst))
		return '\n'.join(lst)

	def has_won_checkers(self, board):
		nos={' ':0,'r':0,'b':0}
		for i in board:
			for m in i:
				nos[m[0]] += 1
		if nos['b'] == 0:
			return 'r'
		elif nos['r'] == 0:
			return 'b'

	@commands.command()
	async def checkers(self, ctx, member:discord.Member):

		board = [
		[' ','b',' ','b',' ','b',' ','b'],
		['b',' ','b',' ','b',' ','b',' '],
		[' ','b',' ','b',' ','b',' ','b'],
		[' ',' ',' ',' ',' ',' ',' ',' '],
		[' ',' ',' ',' ',' ',' ',' ',' '],
		['r',' ','r',' ','r',' ','r',' '],
		[' ','r',' ','r',' ','r',' ','r'],
		['r',' ','r',' ','r',' ','r',' ']
		]
		turn = 'r'
		e = discord.Embed(title='Checkers', description=f"How to play: send the coordinates of the piece you want to move and the direction where it moves in this format `[x][y] [direction]`, eg: `61 ur`\n\nTurn: `{ctx.author.display_name if turn == 'r' else member.display_name}`\n{self.format_checkers_board(board)}", color=discord.Color.blurple()).set_footer(text='Send "end"/"stop"/"cancel" to stop the game')
		msg = await ctx.send(embed=e)
		opts = {"ul": 1, "ur": 2, "dl": 3, "dr": 4}
		while True:
			e = discord.Embed(title='Checkers', description=f"How to play: send the coordinates of the piece you want to move and the direction where it moves in this format `[x][y] [direction]`, eg: `61 ur`\n\nTurn: `{ctx.author.display_name if turn == 'r' else member.display_name}`\n```\n{self.format_checkers_board(board)}\n```", color=discord.Color.blurple()).set_footer(text='Send "end"/"stop"/"cancel" to stop the game')
			await msg.edit(embed=e)
			inp = await self.bot.wait_for('message', check=lambda m: m.author == (ctx.author if turn == 'r' else member) and m.channel == ctx.channel)
			if inp.content.lower() in ['end','stop','cancel']:
				await ctx.send("Ended the game")
				return
			try:
				coors, direction = inp.content.split(' ')[0], inp.content.split(' ')[1]
			except Exception:
				await ctx.send("Invalid syntax: to play your turn select a token and the direction where it goes, eg: `22 dr`", delete_after=5)
				continue
			if direction not in opts:
				await ctx.send(f"Invalid syntax: Correct directions ul (up left), dl (down left), ur (up right), dr (down right)", delete_after=5)
				continue
			elif not len(coors) == 2:
				await ctx.send(f"Invalid syntax: The coordinates entered are invalid", delete_after=5)
				continue
			try:
				await inp.delete()
			except discord.Forbidden:
				pass
			direction = opts[direction]
			if direction == 1:
				inc = (-1,-1)
			if direction == 2:
				inc = (1,-1)
			if direction == 3:
				inc = (-1,1)
			if direction == 4:
				inc = (1,1)
			try:
				x, y = int(coors[0])-1, int(coors[1])-1
			except (IndexError,ValueError):
				await ctx.send("Invalid syntax: The coordinates entered are invalid", delete_after=5)
				continue
			else:
				if x not in range(8) or y not in range(8):
					await ctx.send(f"Invalid syntax: {x+1}{y+1} isnt a valid place on the board", delete_after=5)
			if board[x][y] not in [turn, turn+'k']:
				await ctx.send("Thats not your token", delete_after=5)
				continue
			if board[x][y] == turn+'k':
				try:
					if board[x+inc[1]][y+inc[0]] == ' ':
						if y+inc[0] < 0:
							await ctx.send("Cant go in that direction", delete_after=5)
							continue
						board[x][y] = ' '
						board[x+inc[1]][y+inc[0]] = turn+'k'
					else:
						if board[x+inc[1]*2][y+inc[0]*2]!=' ':
							await ctx.send("Cant do that jump", delete_after=5)
							continue
						board[x][y] = ' '
						board[x+inc[1]][y+inc[0]] = ' '
						board[x+inc[1]*2][y+inc[0]*2] = turn+'k'
				except IndexError:
					await ctx.send("Cant go in that direction", delete_after=5)
					continue
			else:
				if board[x][y] == 'r' and direction in [3,4] or board[x][y] == 'b' and direction in [1,2]:
					await ctx.send('invalid direction', delete_after=5)
					continue
				if board[x][y] == turn:
					try:
						if board[x+inc[1]][y+inc[0]] == ' ':
							if y+inc[0] < 0:
								await ctx.send("Cant go in that direction", delete_after=5)
								continue
							board[x][y] = ' '
							board[x+inc[1]][y+inc[0]] = turn
							if turn == 'r' and x+inc[1] == 0:
								board[x+inc[1]][y+inc[0]] = turn+'k'
							elif turn == 'b' and x+inc[1] == 7:
								board[x+inc[1]][y+inc[0]] = turn+'k'
						elif board[x+inc[1]][y+inc[0]] in [turn,turn+'k']:
							await ctx.send("Cant move there", delete_after=5)
							continue
						else:
							if board[x+inc[1]*2][y+inc[0]*2]!=' ':
								await ctx.send("Cant do that jump")
								continue
							board[x][y] = ' '
							board[x+inc[1]][y+inc[0]] = ' '
							board[x+inc[1]*2][y+inc[0]*2] = turn
							if turn == 'r' and x+inc[1]*2 == 0:
								board[x+inc[1]*2][y+inc[0]*2] = turn+'k'
							elif turn == 'b' and x+inc[1]*2 == 7:
								board[x+inc[1]*2][y+inc[0]*2] = turn+'k'
					except IndexError:
						await ctx.send("Cant move there", delete_after=5)
						continue
			if self.has_won_checkers(board):
				e = discord.Embed(title='Checkers', description=f"Winner: {ctx.author.mention if self.has_won_checkers(board) == 'r' else member.mention}\n{self.format_checkers_board(board)}", color=discord.Color.blurple())
				return await ctx.send(embed=e)
			turn = 'r' if turn == 'b' else 'b'