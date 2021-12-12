import random, discord
from discord.ext import commands

class RPS(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def has_won_rps(self, inp1, inp2):
		dct = {'✂️':'📜','🪨':'✂️','📜':'🪨'}
		if inp1 == inp2:
			return 'Draw'
		elif dct[inp1] == inp2:
			return 'inp1'
		return 'inp2'

	@commands.command()
	async def rps(self, ctx, member:discord.Member=None):
		"""Rock wins against scissors; paper wins against rock; and scissors wins against paper"""
		if not member:
			msg = await ctx.send("Please react with your choice:")
			for i in ['✂️','🪨','📜']:
				await msg.add_reaction(i)
			reaction, _ = await self.bot.wait_for(
					"reaction_add",
					check=lambda r, u: u == ctx.author
					and r.message == msg
					and str(r) in ['✂️', '🪨', '📜'],
				)
			bot_choice = random.choice(['🪨', '📜', '✂️'])
			win = self.has_won_rps(str(reaction), bot_choice)
			await ctx.send(f"{self.bot.user.display_name}: {bot_choice}\n{ctx.author.display_name}: {str(reaction)}\nWinner: {'Draw' if win == 'Draw' else (ctx.author.mention if win == 'inp1' else self.bot.user.mention)}")
		elif member.bot or member == ctx.author:
			return await ctx.send(f"Invalid Syntax: Can't play against {member.display_name}")
		else:
			try:
				msg1 = await ctx.author.send("Please react with your choice:")
				for i in ['✂️','🪨','📜']:
					await msg1.add_reaction(i)
			except discord.Forbidden:
				return await ctx.send(f"I couldnt dm {ctx.author.display_name}")
			try:
				msg2 = await member.send("Please react with your choice:")
				for i in ['✂️','🪨','📜']:
					await msg2.add_reaction(i)
			except discord.Forbidden:
				return await ctx.send(f"I couldnt dm {member.display_name}")

			def check(payload):
				return payload.message_id in [msg1.id,msg2.id] and str(payload.emoji) in ['✂️', '🪨', '📜'] and payload.user_id != self.bot.user.id
			payload = await self.bot.wait_for(
					"raw_reaction_add",
					check=check
				)
			if payload.user_id == ctx.author.id:
				await ctx.send(f"Waiting for {member.display_name}")
				payload2 = await self.bot.wait_for(
						"raw_reaction_add",
						check=lambda p: p.message_id == msg2.id
						and str(payload.emoji) in ['✂️', '🪨', '📜'],
					)
				win = self.has_won_rps(str(payload.emoji), str(payload2.emoji))
				await ctx.send(f"{member.display_name}: {str(payload2.emoji)}\n{ctx.author.display_name}: {str(payload.emoji)}\nWinner: {'Draw' if win == 'Draw' else (ctx.author.mention if win == 'inp1' else member.mention)}")
			else:
				await ctx.send(f"Waiting for {ctx.author.display_name}")
				payload2 = await self.bot.wait_for(
						"raw_reaction_add",
						check=lambda p: p.message_id == msg1.id
						and str(payload.emoji) in ['✂️', '🪨', '📜'],
					)
				win = self.has_won_rps(str(payload2.emoji), str(payload.emoji))
				await ctx.send(f"{member.display_name}: {str(payload.emoji)}\n{ctx.author.display_name}: {str(payload2.emoji)}\nWinner: {'Draw' if win == 'Draw' else (ctx.author.mention if win == 'inp1' else member.mention)}")