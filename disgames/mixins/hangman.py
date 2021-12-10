import discord, random
from discord.ext import commands

class Hangman(commands.Cog):
    """
    Hang man command
    """

    def __init__(self, bot):
        self.bot = bot

    def make_hangman(self, errors):
        head = "()" if errors > 0 else "  "
        torso = "||" if errors > 1 else "  "
        left_arm = "/" if errors > 2 else " "
        right_arm = "\\" if errors > 3 else " "
        left_leg = "/" if errors > 4 else " "
        right_leg = "\\" if errors > 5 else " "
        return f"```\n {head}\n{left_arm}{torso}{right_arm}\n {left_leg}{right_leg}\n```"

    def _show_guesses(self, embed, guesses):
        if guesses:
            embed.add_field(
                name="Guesses",
                value="".join(f":regional_indicator_{i}:" for i in guesses),
                inline=False,
            )

    @commands.command("hangman", aliases=["hm"])
    async def command(self, ctx: commands.Context):
        """Try to guess the word"""
        try:
            with open('./words.txt', "r") as f:
                words = [s.lower() for s in f.read().splitlines() if len(s) >= 4 and len(s) <= 6]
        except FileNotFoundError:
            return await ctx.send("Could not find the words.txt file")
        word = list(random.choice(words))
        guesses = []
        errors = 0
        revealed_message = "🟦 " * len(word)
        embed = discord.Embed(color=discord.Color.blurple()).set_footer(text='Send "end"/"stop"/"cancel" to stop the game')
        embed.add_field(
            name="Hangman", value=self.make_hangman(errors), inline=False
        )
        embed.add_field(
            name="Word",
            value="".join(revealed_message.split(" ")),
            inline=False,
        )
        msg = await ctx.send(embed=embed)

        while True:
            embed = discord.Embed(color=discord.Color.blurple()).set_footer(text='Send "end"/"stop"/"cancel" to stop the game')
            embed.add_field(
                name="Word",
                value="".join(f":regional_indicator_{i}:" for i in word),
                inline=False,
            )
            message: discord.Message = await ctx.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author
                and m.channel == ctx.channel,
            )
            if message.content.lower() in ['end','stop','cancel']:
                return await ctx.send("Ended the game")
            if len(message.content.lower()) > 1:
                if message.content.lower() == "".join(word):
                    embed.add_field(
                        name="Hangman",
                        value=self.make_hangman(errors),
                        inline=False,
                    )
                    self._show_guesses(embed, guesses)
                    embed.add_field(
                        name="Result:", value="You've won!", inline=False
                    )
                    return await msg.edit(embed=embed)
                else:
                    await ctx.send(
                        "Invalid Syntax: your guess can't be more than 1 letter long or the word itself"
                    )
            elif message.content.lower().isalpha():
                guesses.append(message.content.lower())
                if message.content.lower() not in word:
                    errors += 1
                if errors == 6:
                    embed = discord.Embed(color=discord.Color.blurple())
                    embed.add_field(
                        name="Hangman",
                        value=self.make_hangman(errors),
                        inline=False,
                    )
                    self._show_guesses(embed, guesses)
                    embed.add_field(
                        name="Result:",
                        value=f"You lost :pensive:\n word was {''.join(word)}",
                        inline=False,
                    )
                    return await msg.edit(embed=embed)
                revealed_message = revealed_message.split(" ")
                for i in range(len(word)):
                    if word[i] == message.content.lower():
                        revealed_message[i] = f":regional_indicator_{word[i]}:"
                revealed_message = " ".join(revealed_message)
                if "🟦 " not in revealed_message:
                    embed.add_field(
                        name="Hangman",
                        value=self.make_hangman(errors),
                        inline=False,
                    )
                    self._show_guesses(embed, guesses)
                    embed.add_field(
                        name="Result:", value="You've won!", inline=False
                    )
                    return await msg.edit(embed=embed)
                else:
                    embed = discord.Embed(color=discord.Color.blurple()).set_footer(text='Send "end"/"stop"/"cancel" to stop the game')
                    embed.add_field(
                        name="Hangman",
                        value=self.make_hangman(errors),
                        inline=False,
                    )
                    embed.add_field(
                        name="Word",
                        value="".join(revealed_message.split(" ")),
                        inline=False,
                    )
                    self._show_guesses(embed, guesses)
                    await msg.edit(embed=embed)
            else:
                await ctx.send(
                    f"Invalid Syntax: {message.content.lower()} is not a letter"
                )