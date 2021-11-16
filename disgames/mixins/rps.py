import random, discord
from discord.ext import commands

class RPS(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.scissors = '✂️'
		self.rock = '🪨'
		self.paper = '📜'

	def won(self, inp1, inp2):
		dct = {self.scissors:self.paper,self.rock:self.scissors,self.paper:self.paper}
		if inp1 == inp2:
			return 'Draw'
		elif dct[inp1] == inp2:
			return 'inp1'
		return 'inp2'

	@commands.command()
	async def rps(self, ctx, member:discord.Member=None):
		if not member:
			msg = await ctx.send("Please react with your choice:")
			for i in [self.scissors,self.rock,self.paper]:
				await msg.add_reaction(i)
			reaction, _ = await self.bot.wait_for(
					"reaction_add",
					check=lambda r, u: u == ctx.author
					and r.message == msg
					and str(r) in [self.scissors, self.rock, self.paper],
				)
			bot_choice = random.choice([self.rock, self.paper, self.scissors])
			win = self.won(str(reaction), bot_choice)
			await ctx.send(f"{self.bot.user.display_name}: {bot_choice}\n{ctx.author.display_name}: {str(reaction)}\nWinner: {'Draw' if win == 'Draw' else (ctx.author.mention if win == 'inp1' else self.bot.user.mention)}")
		elif member.bot or member == ctx.author:
			return await ctx.send(f"Invalid Syntax: Can't play against {member.display_name}")
		else:
			try:
				msg1 = await ctx.author.send("Please react with your choice:")
				for i in [self.scissors,self.rock,self.paper]:
					await msg1.add_reaction(i)
			except discord.Forbidden:
				await ctx.send(f"I couldnt dm {ctx.author.display_name}")
			try:
				msg2 = await member.send("Please react with your choice:")
				for i in [self.scissors,self.rock,self.paper]:
					await msg2.add_reaction(i)
			except discord.Forbidden:
				await ctx.send(f"I couldnt dm {member.display_name}")
			reaction1, user = await self.bot.wait_for(
					"reaction_add",
					check=lambda r, u: u in [ctx.author,member]
					and r.message in [msg1,msg2]
					and str(r) in [self.scissors, self.rock, self.paper],
				)
			if user == ctx.author:
				await ctx.send(f"Waiting for {member.display_name}")
				reaction2, _ = await self.bot.wait_for(
						"reaction_add",
						check=lambda r, u: u == member
						and r.message == msg2
						and str(r) in [self.scissors, self.rock, self.paper],
					)
				win = self.won(str(reaction1), str(reaction2))
				await ctx.send(f"{member.display_name}: {str(reaction2)}\n{ctx.author.display_name}: {str(reaction1)}\nWinner: {'Draw' if win == 'Draw' else (ctx.author.mention if win == 'inp1' else member.mention)}")
			else:
				await ctx.send(f"Waiting for {ctx.author.display_name}")
				reaction2, _ = await self.bot.wait_for(
						"reaction_add",
						check=lambda r, u: u == ctx.author
						and r.message == msg1
						and str(r) in [self.scissors, self.rock, self.paper],
					)
				win = self.won(str(reaction2), str(reaction1))
				await ctx.send(f"{member.display_name}: {str(reaction1)}\n{ctx.author.display_name}: {str(reaction2)}\nWinner: {'Draw' if win == 'Draw' else (ctx.author.mention if win == 'inp1' else member.mention)}")