import discord, random
from discord.ext import commands
import aiohttp


class Hangman(commands.Cog):
    """
    Hang man command
    """

    def __init__(self, bot):
        self.bot = bot

    @property
    def _url(self):
        return "https://raw.githubusercontent.com/andrewthederp/Disgames/main/disgames/mixins/words.txt"

    @property
    def _session(self):
        return self.bot.http._HTTPClient__session

    async def _request(self):
        response = await self._session.get(self._url)
        return await response.text()

    async def _get_word(self):
        """Returns a random word"""
        try:
            with open("./words.txt", "r") as file:
                data = file.read().splitlines()
                word = random.choice(data)
        except Exception:
            words = await self._request()
            with open("./words.txt", "w") as file:
                file.write("\n".join([word[:-2] for word in words.split("\n")]))
            with open("./words.txt", "r") as file:
                data = file.read().splitlines()
                word = random.choice(data)
        finally:
            return str(word)

    def make_hangman(self, errors):
        """A function to make depending on the amount of errors made"""
        head = "()" if errors > 0 else "  "
        torso = "||" if errors > 1 else "  "
        left_arm = "/" if errors > 2 else " "
        right_arm = "\\" if errors > 3 else " "
        left_leg = "/" if errors > 4 else " "
        right_leg = "\\" if errors > 5 else " "
        return (
            f"```\n {head}\n{left_arm}{torso}{right_arm}\n {left_leg}{right_leg}\n```"
        )

    def _show_guesses(self, embed, guesses):
        """Show all the guesses made so far"""
        if guesses:
            embed.add_field(
                name="Guesses",
                value="".join(f":regional_indicator_{i}:" for i in guesses),
                inline=False,
            )

    @commands.command("hangman", aliases=["hm"])
    async def command(self, ctx: commands.Context):
        word = await self._get_word()
        word = str(word).replace("\n", "")
        word = list(word)

        guesses = []
        errors = 0
        revealed_message = "🟦 " * len(word)
        embed = discord.Embed(color=discord.Color.blurple())
        embed.add_field(name="Hangman", value=self.make_hangman(errors), inline=False)
        embed.add_field(
            name="Word",
            value="".join(revealed_message.split(" ")),
            inline=False,
        )
        msg = await ctx.send(embed=embed)

        while True:
            embed = discord.Embed(color=discord.Color.blurple())
            embed.add_field(
                name="Word",
                value="".join(f":regional_indicator_{i}:" for i in word),
                inline=False,
            )
            message: discord.Message = await ctx.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
            )
            if message.content.lower() in ["end", "stop", "cancel"]:
                return await ctx.send("Ended the game")

            if message.content in guesses:
                await ctx.send("You already guessed that", delete_after=5)
                continue

            if len(message.content.lower()) > 1:
                if message.content.lower() == "".join(word):
                    embed.add_field(
                        name="Hangman",
                        value=self.make_hangman(errors),
                        inline=False,
                    )
                    self._show_guesses(embed, guesses)
                    embed.add_field(name="Result:", value="You've won!", inline=False)
                    return await msg.edit(embed=embed)
                else:
                    errors += 1
                    await ctx.send("Uhoh, that was not the word", delete_after=5)
                    embed = discord.Embed(color=discord.Color.blurple())
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
            elif message.content.lower().isalpha():
                guesses.append(message.content)
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
                    embed.add_field(name="Result:", value="You've won!", inline=False)
                    return await msg.edit(embed=embed)
                else:
                    embed = discord.Embed(color=discord.Color.blurple())
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
