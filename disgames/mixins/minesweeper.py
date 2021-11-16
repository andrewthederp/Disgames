import discord
from discord.ext import commands
import random

class Minesweeper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_boards(self, columns, rows, bombs):
        grid = [[0 for _ in range(columns)] for _ in range(rows)]
        num = 0
        while num < bombs:
            x = random.randint(0, columns - 1)
            y = random.randint(0, rows - 1)
            if grid[y][x] == 0:
                grid[y][x] = "B"
                num += 1

        pos_x = 0
        pos_y = 0
        while pos_x * pos_y < columns * rows and pos_y < rows:
            adj_sum = 0
            for (adj_y, adj_x) in [
                (0, 1),
                (0, -1),
                (1, 0),
                (-1, 0),
                (1, 1),
                (-1, 1),
                (1, -1),
                (-1, -1),
            ]:
                try:
                    if (
                        grid[adj_y + pos_y][adj_x + pos_x] == "B"
                        and adj_y + pos_y > -1
                        and adj_x + pos_x > -1
                    ):
                        adj_sum += 1
                except IndexError:
                    pass
            if grid[pos_y][pos_x] != "B":
                grid[pos_y][pos_x] = adj_sum
            if pos_x == columns - 1:
                pos_x = 0
                pos_y += 1
            else:
                pos_x += 1

        visible_board = [[" " for _ in range(columns)] for _ in range(rows)]
        return grid, visible_board

    def format_board(self, board):
        dct = {"B": "💣", "f": "🚩", " ": "🟦", "0": "⬛","10":":keycap_ten:"}
        for i in range(1, 10):
            dct[str(i)] = f"{i}\N{variation selector-16}\N{combining enclosing keycap}"
        lst = [f":stop_button:{''.join([dct[str(i+1)] for i in range(len(board[0]))])}"]
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
                if board[x][y] == "B":
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

    def has_won(self, visible_board, board):
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
    async def minesweeper(self, ctx, columns=None, rows=None, bombs=None):
        if columns is None or rows is None and bombs is None:
            if columns is not None or rows is not None or bombs is not None:
                return await ctx.send(
                    f"Invalid syntax: That is not formatted properly, the proper format is {ctx.prefix}minesweeper <columns> <rows> <bombs>\n\nYou can give me nothing for random columns, rows, bombs."
                )
            else:
                columns = random.randint(4, 10)
                rows = random.randint(4, 10)
                bombs = round(random.randint(5, round(((columns * rows - 1) / 2.5))))
        try:
            columns = int(columns)
            rows = int(rows)
            bombs = int(bombs)
        except ValueError:
            return await ctx.send("The columns, rows, bombs have to be numbers")

        if columns > 10 or rows > 10:
            return await ctx.send("columns/rows cant be bigger than 10")
        elif columns < 4 or rows < 4:
            return await ctx.send("columns/rows cant be smaller than 4")
        elif columns * rows > 10 * 10:
            return await ctx.send("Board is too big")
        elif columns * rows < 4 * 4:
            return await ctx.send("Board is too small")
        elif bombs >= rows * columns:
            return await ctx.send(
                "you lost :pensive: there were more bombs than indexes on the board"
            )

        grid, visible_board = self.create_boards(columns, rows, bombs)

        em = discord.Embed(
            title="Minesweeper",
            description=self.format_board(visible_board),
            color=discord.Color.blurple(),
        )
        msg = await ctx.send(embed=em)
        while True:
            m = await ctx.send("Send the coordinates, eg: `reveal 35 17 59`")
            inp = await self.bot.wait_for(
                "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
            )
            await m.delete()
            try:
                await inp.delete()
            except discord.Forbidden:
                pass
            if inp.content.lower() in ['end','stop','cancel']:
                return await ctx.send("Ended the game")
            lst = inp.content.split()
            type_ = lst[0]
            xy = lst[1:]
            xy = tuple(xy)
            for x, y in xy:
                try:
                    x, y = int(x) - 1, int(y) - 1
                except ValueError:
                    await ctx.send(
                        f"Invalid syntax: either {x} or {y} wasnt a number, please use numbers next time",
                        delete_after=5
                    )
                    continue
                if x > len(grid) or x <= -1 or y > len(grid[0]) or y <= -1:
                    await ctx.send(
                        f"Invalid syntax: {x+1}{y+1} isnt a valid place on the board",
                        delete_after=5,
                    )
                    continue
                if type_.lower() in ["reveal", "r"]:
                    if grid[x][y] == "B":
                        await ctx.send(
                            f"{ctx.author.mention} just lost Minesweeper! :pensive:",
                            embed=discord.Embed(
                                title="Minesweeper",
                                description=self.format_board(
                                    self.reveal_all(visible_board, grid)
                                ),
                                color=discord.Color.blurple(),
                            ),
                        )
                        return
                    else:
                        if visible_board[x][y] != " ":
                            await ctx.send(
                                f"Invalid syntax: {x+1}{y+1} is already revealed or flagged",
                                delete_after=5,
                            )
                            continue
                        visible_board[x][y] = str(grid[x][y])
                        if visible_board[x][y] == "0":
                            visible_board = self.reveal_zeros(visible_board, grid, x, y)
                        grid[x][y] = "r"
                elif type_.lower() in ["flag", "f"]:
                    if visible_board[x][y] != " ":
                        await ctx.send(
                            f"Invalid syntax: {x+1}{y+1} is already revealed or flagged",
                            delete_after=5,
                        )
                        continue
                    visible_board[x][y] = "f"
                else:
                    await ctx.send(
                        f"Invalid syntax: {type_} isnt a valid move type",
                        delete_after=5,
                    )
                if self.has_won(visible_board, grid):
                    em = discord.Embed(
                        title="Minesweeper",
                        description=self.format_board(
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
                        description=self.format_board(visible_board),
                        color=discord.Color.blurple(),
                    )
                )
