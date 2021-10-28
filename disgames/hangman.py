import discord
from discord.ext import commands
from .utils import format_board, edit_board
from .board import Board

class Hangman:
    def make_hangman(self, errors):
        head = '()' if errors > 0 else '  '
        torso = '||' if errors > 1 else '  '
        left_arm = '/' if errors > 2 else ' '
        right_arm = '\\' if errors > 3 else ' '
        left_leg = '/' if errors > 4 else ' '
        right_leg = '\\' if errors > 5 else ' '
        return f"```\n {head}\n{left_arm}{torso}{right_arm}\n {left_leg}{right_leg}\n```"

    def _show_guesses(self, embed, guesses):
        if guesses:
            embed.add_field(name="Guesses", value=''.join(f':regional_indicator_{i}:' for i in guesses))

    @commands.command("hangman", aliases=['hm'])
    async def command(self, ctx: commands.Context):
        word = 'hello'
        word = list(word)
        guesses = []
        errors = 0
        revealed_message = '🟦'*len(word)
        embed = discord.Embed()
        embed.add_field(name='Hangman', value=self.make_hangman(errors))
        embed.add_field(name='Word', value=revealed_message)
        msg = await ctx.send(embed=embed)

        while True:
            embed = discord.Embed()
            embed.add_field(name='Hangman', value=self.make_hangman(errors))
            embed.add_field(name='Word', value=''.join(f':regional_indicator_{i}:' for i in word))
            msg: discord.Message = await ctx.bot.wait_for('message', check = lambda m: m.author == ctx.author and m.channel == ctx.channel)
            if len(msg.content.lower()) > 1:
                if msg.content.lower() == ''.join(word):
                    # embed = discord.Embed()
                    # embed.add_field(name='Hangman', value=self.make_hangman(errors))
                    # embed.add_field(name='Word', value=''.join(f':regional_indicator_{i}:' for i in word))
                    self._show_guesses(embed, guesses)
                    embed.add_field(name="Result:", value="You've won!")
                    return await msg.edit(embed = embed)
                else:
                    await ctx.send("Invalid Syntax: your guess can't be more than 1 letter long or the word itself")
            elif msg.content.lower().isalpha():
                guesses.append(msg.content)
                if msg.content.lower() not in word:
                    errors += 1
                if errors == 5:
                        # embed = discord.Embed()
                        # embed.add_field(name='Hangman', value=self.make_hangman(errors))
                        # embed.add_field(name='Word', value=''.join(f':regional_indicator_{i}:' for i in word))
                    if guesses:
                        embed.add_field(name="Guesses", value=''.join(i if i == '🟦' else f':regional_indicator_{i}:' for i in revealed_message))
                    embed.add_field(name="Result:", value=f"You lost :pensive:\n word was {''.join(word)}")
                    return await msg.edit(embed = embed)
                revealed_message = list(revealed_message)
                for i in range(len(word)):
                    if word[i] == msg.content.lower():
                        revealed_message[i] = f':regional_indicator_{word[i]}:'
                    elif revealed_message[i] == '🟦':
                        revealed_message[i] = '🟦'
                revealed_message = ''.join(revealed_message)
                if '🟦' not in revealed_message:
                        # embed = discord.Embed()
                        # embed.add_field(name='Hangman', value=self.make_hangman(errors))
                        # embed.add_field(name='Word', value=''.join(f':regional_indicator_{i}:' for i in word))
                    self._show_guesses(embed, guesses)
                    embed.add_field(name="Result:", value="You've won!")
                    return await msg.edit(embed = embed)
                else:
                    embed = discord.Embed()
                    embed.add_field(name='Hangman', value=self.make_hangman(errors))
                    embed.add_field(name='Word', value=''.join(i if i == '🟦' else f':regional_indicator_{i}:' for i in revealed_message))
                    self._show_guesses(embed, guesses)
                    await msg.edit(embed = embed)
            else:
                await ctx.send(f"Invalid Syntax: {msg.content.lower()} is not a letter")
