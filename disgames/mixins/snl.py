import random
import discord
from discord.ext import commands

class SNL(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.snakes_and_ladders = {"s": [(7,2), (6,6), (4,8), (3, 1), (1, 8), (0, 5)], 'l':[(9,9), (8, 4), (7, 0), (6, 5), (5, 3), (2, 0)]}

	def format_snl_board(self, board):
		dct = {' ':'⬛', 's':'🐍', 'l':'🪜', 'p1':'🔴', 'p2':'🟡', 'p3':'🟢', 'p4':'🔵'}
		lst = [''.join([dct[column] for column in row]) for row in board]
		return '\n'.join(lst)

	def create_board(self):
		board = [[' ' for _ in range(10)] for _ in range(10)]
		for key in self.snakes_and_ladders:
			for indx in self.snakes_and_ladders[key]:
				board[indx[0]][indx[1]] = key
		board[9][0] = "p1"
		return board

	@commands.command()
	async def snl(self, ctx, players: commands.Greedy[discord.Member]=[]):
		for player in players:
			if player == ctx.author:
				players.remove(player)
		if not players:
			players.append(self.bot.user)
		players.append(ctx.author)
		if len(players) > 4:
			return await ctx.send("Can't have more than 4 people playing")
		tokens = {'p1':'🔴', 'p2':'🟡', 'p3':'🟢', 'p4':'🔵'}
		indexes = {player: [9,0] for player in players}
		board = self.create_board()
		player_string = ' '.join([
		    f"{player.mention}: {tokens['p'+str(num)]}"
		    for num, player in enumerate(players, start=1)
		])
		embed = discord.Embed(title='Snakes and Ladders', description=f"React to '🎲' to roll your dice\n\n{player_string}\n{self.format_snl_board(board)}", color=discord.Color.blurple())
		msg = await ctx.send(embed=embed)
		await msg.add_reaction('🎲')
		await msg.add_reaction('🏳️')
		current_player = 0
		leaderboard = []
		while True:
			if len(players) == 1:
				leaderboard.append(players[0])
				break
			player = players[current_player]
			index = indexes[player]
			number = random.randint(1,6)
			await msg.edit(embed = discord.Embed(title='Snakes and Ladders', description=f"React to '🎲' to roll your dice\n\n{player_string}\nturn: `{player.display_name}`\n{self.format_snl_board(board)}", color=discord.Color.blurple()))
			if not player.bot:
				reaction, user = await self.bot.wait_for('reaction_add', check = lambda r, u: str(r) in ['🎲','🏳️'] and r.message == msg and u in players)
				try:
					await msg.remove_reaction(str(reaction), user)
				except discord.Forbidden:
					pass
				if str(reaction) == '🏳️':
					players.remove(user)
					await ctx.send(f"{user.mention} leaves")
				elif user != player:
					continue
			await ctx.send(f'{player.mention} rolled a {number}', delete_after=5)
			board[index[0]][index[1]] = ' '
			past_number = index[1]
			if index[0]%2:
				index[1] += number
			elif index[0] != 0 or index[1] - number >= 0:
				index[1] -= number
			if (index[1]) > 9 or (index[1]) < 0 and index[1] != 0:
				index[0] -= 1
				if index[0]%2:
					index[1] = (number-past_number)-1
				else:
					index[1] = 10-((past_number+number)-9)

			dct = {'72':[9, 1],'66':[8, 5], '48':[7, 9], '31':[5, 2], '18':[3, 7], '05':[2, 6], '99':[6, 7], '84':[6, 3], '70':[5, 0], '65':[4, 6], '53':[2, 4], '20':[0, 1]}
			for key in self.snakes_and_ladders:
				for indx in self.snakes_and_ladders[key]:
					board[indx[0]][indx[1]] = key
			if str(index[0])+str(index[1]) in dct:
				await ctx.send(f"{player.mention} has {'hit a snake' if tuple(index) in self.snakes_and_ladders['s'] else 'went up a ladder'}", delete_after=5)
				indexes[player] = dct[str(index[0])+str(index[1])]
				index = indexes[player]
			elif index == [0, 0]:
				await ctx.send(f"{player.mention} won!!!")
				players.remove(player)
				leaderboard.append(player)
			current_player += 1
			if current_player == len(players):
				current_player = 0
			for num, player in enumerate(players, start=1):
				board[indexes[player][0]][indexes[player][1]] = 'p'+str(num)
		winning_string = ''
		for num, player in enumerate(leaderboard, start=1):
			medal = None
			if num == 1:
				medal = '🥇'
			elif num == len(leaderboard):
				medal = 'Looser'
			elif num == 2:
				medal = '🥈'
			elif num == 3:
				medal = '🥉'
			winning_string += f'\n{player.display_name}: {medal}'
		await ctx.send(winning_string)
