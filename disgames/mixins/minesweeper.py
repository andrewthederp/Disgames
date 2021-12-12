import discord
from discord.ext import commands
import random
import asyncio

class Minesweeper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_minesweeper_boards(self):
        board = [["b" if random.random() <= .14 else "n" for _ in range(10)] for _ in range(10)]
        board[random.randint(0, 9)][random.randint(0, 9)] = "n"
        for x, row in enumerate(board):
            for y, cell in enumerate(row):
                if cell == "n":
                    bombs = 0
                    for x_, y_ in self.get_neighbours(x, y):
                        try:
                            if board[x_][y_] == "b":
                                bombs += 1
                        except IndexError:
                            pass
                    board[x][y] = bombs

        visible_board = [[" " for _ in range(10)] for _ in range(10)]
        return board, visible_board

    def get_coors(self, coordinate):
        if len(coordinate) not in (2, 3):
            raise commands.BadArgument("Invalid syntax: invalid coordinate provided.")

        coordinate = coordinate.lower()
        if coordinate[0].isalpha():
            digit = coordinate[1:]
            letter = coordinate[0]
        else:
            digit = coordinate[:-1]
            letter = coordinate[-1]

        if not digit.isdecimal():
            raise commands.BadArgument

        x = int(digit) - 1
        y = ord(letter) - ord("a")

        if (not 0 <= x <= 10) or (not 0 <= y <= 10):
            raise commands.BadArgument("Invalid syntax: Entered coordinates aren't on the board")
        return x, y

    def format_minesweeper_board(self, board):
        dct = {"b": "💣", "f": "🚩", " ": "🟦", "0": "⬛", '10':'🔟'}
        for i in range(1, 10):
            dct[str(i)] = f"{i}\N{variation selector-16}\N{combining enclosing keycap}"
        lst = [f":stop_button::regional_indicator_a::regional_indicator_b::regional_indicator_c::regional_indicator_d::regional_indicator_e::regional_indicator_f::regional_indicator_g::regional_indicator_h::regional_indicator_i::regional_indicator_j:"]
        for num, i in enumerate(board, start=1):
            scn_lst = [dct[str(num)]]
            for thing in i:
                scn_lst.append(str(thing).replace(str(thing), dct[str(thing)]))
            lst.append("".join(scn_lst))
        return "\n".join(lst)

    def get_bombs(self, board):
        lst = []
        for x in range(len(board)):
            for y in range(len(board[x])):
                if board[x][y] == "b":
                    lst.append(f"{x}{y}")
        return lst

    def get_neighbours(self, x, y):
        for x_ in [x - 1, x, x + 1]:
            for y_ in [y - 1, y, y + 1]:
                if x_ != -1 and x_ != 11 and y_ != -1 and y_ != 11:
                    yield x_, y_

    def reveal_zeros(self, visible_board, grid, x, y):
        for x_, y_ in self.get_neighbours(x, y):
            try:
                if visible_board[x_][y_] != " ":
                    continue
                visible_board[x_][y_] = str(grid[x_][y_])
                if grid[x_][y_] == 0:
                    self.reveal_zeros(visible_board, grid, x_, y_)
                grid[x_][y_] = "r"
            except IndexError:
                continue
        return visible_board

    def has_won_minesweeper(self, visible_board, board):
        num = 0
        bombs = self.get_bombs(board)
        for x in board:
            for y in x:
                if y == "r":
                    num += 1
        if num == (len(board) * len(board[0]) - len(bombs)):
            return True
        num = 0
        for i in bombs:
            if visible_board[int(i[0])][int(i[1])] == "f":
                num += 1
        if num == len(bombs):
            return True

    def reveal_all(self, visible_board, board):
        for x in range(len(visible_board)):
            for y in range(len(visible_board[x])):
                if visible_board[x][y] == " ":
                    visible_board[x][y] = board[x][y]
        return visible_board

    @commands.command(aliases=['ms'])
    async def minesweeper(self, ctx):
        """a square board containing hidden "mines" or bombs without detonating any of them, with help from clues about the number of neighbouring mines in each field."""
        grid, visible_board = self.create_minesweeper_boards()

        em = discord.Embed(
            title="Minesweeper",
            description=f"to reveal a place send the coordinates, eg: `reveal d5 7a 3h`\nto flag a place send the coordinates, eg: `flag d5 7a 3h`\n\n{self.format_minesweeper_board(visible_board)}",
            color=discord.Color.blurple(),
        ).set_footer(text='Send "end"/"stop"/"cancel" to stop the game')
        msg = await ctx.send(embed=em)
        while True:
            inp = await self.bot.wait_for(
                "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
            )
            try:
                await inp.delete()
            except discord.Forbidden:
                pass
            if inp.content.lower() in ['end','stop','cancel']:
                return await ctx.send("Ended the game")
            lst = inp.content.split()
            type_ = lst[0]
            xy = lst[1:]
            for coors in xy:
                try:
                    x, y = self.get_coors(coors)
                except Exception as e:
                    await ctx.send(e)
                    continue
                if type_.lower() in ["reveal", "r"]:
                    if grid[x][y] == "b":
                        return await ctx.send(
                            f"{ctx.author.mention} just lost Minesweeper! :pensive:",
                            embed=discord.Embed(
                                title="Minesweeper",
                                description=self.format_minesweeper_board(
                                    self.reveal_all(visible_board, grid)
                                ),
                                color=discord.Color.blurple(),
                            ),
                        )
                    else:
                        if visible_board[x][y] == "f":
                            continue
                        elif visible_board[x][y] != ' ':
                            await ctx.send(f"Invalid Syntax: {coors} is already revealed", delete_after=5)
                            continue
                        visible_board[x][y] = str(grid[x][y])
                        if visible_board[x][y] == "0":
                            visible_board = self.reveal_zeros(visible_board, grid, x, y)
                        grid[x][y] = "r"
                elif type_.lower() in ["flag", "f"]:
                    if visible_board[x][y] != ' ':
                        await ctx.send(
                            f"Invalid syntax: {coors} is already revealed or flagged",
                            delete_after=5,
                        )
                        continue
                    visible_board[x][y] = "f"
                else:
                    await ctx.send(
                        f"Invalid syntax: {type_} isnt a valid move type",
                        delete_after=5,
                    )
                if self.has_won_minesweeper(visible_board, grid):
                    em = discord.Embed(
                        title="Minesweeper",
                        description=self.format_minesweeper_board(
                            self.reveal_all(visible_board, grid)
                        ),
                        color=discord.Color.blurple(),
                    )
                    await ctx.send(
                        f":tada: {ctx.author.mention} just won Minesweeper! :tada:",
                        embed=em
                    )
                    return
                await msg.edit(
                    embed=discord.Embed(
                        title="Minesweeper",
                        description=f"to reveal a place send the coordinates, eg: `reveal d5 7a 3h`\nto flag a place send the coordinates, eg: `flag d5 7a 3h`\n\n{self.format_minesweeper_board(visible_board)}",
                        color=discord.Color.blurple(),
                    ).set_footer(text='Send "end"/"stop"/"cancel" to stop the game')
                )