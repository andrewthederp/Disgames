import discord
from discord.ext import commands
import random

try:
    class RPSButton(discord.ui.Button):
        def __init__(self, emoji):
            self.conversion = {"✂️":'Scissors',"📜":'Paper',"🪨":"Rock"}
            super().__init__(label=self.conversion[emoji], emoji=emoji, style=discord.ButtonStyle.primary)

        async def callback(self, interaction):
            view = self.view
            if not interaction.user in view.plays:
                return await interaction.response.send_message("You're not in this game", ephemeral=True)
            elif view.plays[interaction.user]:
                return await interaction.response.send_message("You already chose", ephemeral=True)
            view.plays[interaction.user] = str(self.emoji)
            if view.player2.bot:
                view.plays[view.player2] = random.choice(list(self.conversion))
            try:
                winner = view.has_won_rps_buttons(view.player1, view.player2)
            except KeyError:
                return await interaction.response.send_message(f"Waiting for {view.player2.mention if interaction.user == view.player1 else view.player1.mention}", ephemeral=True)
            else:
                view.stop()
                view.clear_items()
                return await interaction.response.edit_message(content=f"{view.player1.mention}: {view.plays[view.player1]}\n{view.player2.mention}: {view.plays[view.player2]}\n\nWinner: {winner}", view=view)

    class RPSView(discord.ui.View):
        def __init__(self, player1, player2):
            super().__init__(timeout=None)
            for emoji in ["✂️", "📜", "🪨"]:
                self.add_item(RPSButton(emoji))
            self.plays = {player1:'',player2:''}
            self.player1 = player1
            self.player2 = player2

        def has_won_rps_buttons(self, player1, player2):
            """Returns the winner"""
            if not self.plays[player1] or not self.plays[player2]:
                raise KeyError
            dct = {"✂️":"📜","🪨":"✂️","📜":"🪨"}
            if dct[self.plays[player1]] == dct[self.plays[player2]]:
                return "Draw"
            elif dct[self.plays[player1]] == self.plays[player2]:
                return player1.mention
            return player2.mention

    class RPSButtons(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        @commands.command()
        async def rps(self, ctx, member:discord.Member=None):
            if member and (member.bot or member == ctx.author):
                return await ctx.send("Invalid syntax: can't play again "+member.display_name)
            await ctx.send('Rock Paper Scissors', view=RPSView(ctx.author, member or self.bot.user))

except AttributeError:
    class RPSButtons:
        pass