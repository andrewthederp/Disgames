import discord, random
from discord.ext import commands


class Connect4(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def format_connect4_board(self, board):
        """Format the minesweeper board"""
        toDisplay = ""
        dct = {"b": "🔵", "r": "🔴", " ": "⬛", "R": "♦️", "B": "🔷"}
        for y in range(6):
            for x in range(6):
                toDisplay += dct[board[y][x]]
            toDisplay += dct[board[y][6]] + "\n"
        toDisplay += "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣"
        return toDisplay

    def has_won_connect4(self, board, is_bot=False):
        """Checks if game is over"""
        height = 6
        width = 7
        for x in range(height):
            for y in range(width - 3):
                if (
                    board[x][y] == board[x][y + 1]
                    and board[x][y] == board[x][y + 2]
                    and board[x][y] == board[x][y + 3]
                    and board[x][y] != " "
                ):
                    if not is_bot:
                        if board[x][y] == "b":
                            board[x][y] = "B"
                            board[x][y + 1] = "B"
                            board[x][y + 2] = "B"
                            board[x][y + 3] = "B"
                        elif board[x][y] == "r":
                            board[x][y] = "R"
                            board[x][y + 1] = "R"
                            board[x][y + 2] = "R"
                            board[x][y + 3] = "R"
                    return True, board, "in a horizontal row", board[x][y].lower()
        for x in range(height - 3):
            for y in range(width):
                if (
                    board[x][y] == board[x + 1][y]
                    and board[x][y] == board[x + 2][y]
                    and board[x][y] == board[x + 3][y]
                    and board[x][y] != " "
                ):
                    if not is_bot:
                        if board[x][y] == "b":
                            board[x][y] = "B"
                            board[x + 1][y] = "B"
                            board[x + 2][y] = "B"
                            board[x + 3][y] = "B"
                        elif board[x][y] == "r":
                            board[x][y] = "R"
                            board[x + 1][y] = "R"
                            board[x + 2][y] = "R"
                            board[x + 3][y] = "R"
                    return True, board, "in a vertical row", board[x][y].lower()
        for x in range(height - 3):
            for y in range(width - 3):
                if (
                    board[x][y] == board[x + 1][y + 1]
                    and board[x][y] == board[x + 2][y + 2]
                    and board[x][y] == board[x + 3][y + 3]
                    and board[x][y] != " "
                ):
                    if not is_bot:
                        if board[x][y] == "b":
                            board[x][y] = "B"
                            board[x + 1][y + 1] = "B"
                            board[x + 2][y + 2] = "B"
                            board[x + 3][y + 3] = "B"
                        elif board[x][y] == "r":
                            board[x][y] = "R"
                            board[x + 1][y + 1] = "R"
                            board[x + 2][y + 2] = "R"
                            board[x + 3][y + 3] = "R"
                    return True, board, "on a \ diagonal", board[x][y].lower()
        for x in range(height - 3):
            for y in range(3, width):
                if (
                    board[x][y] == board[x + 1][y - 1]
                    and board[x][y] == board[x + 2][y - 2]
                    and board[x][y] == board[x + 3][y - 3]
                    and board[x][y] != " "
                ):
                    if not is_bot:
                        if board[x][y] == "b":
                            board[x][y] = "B"
                            board[x + 1][y - 1] = "B"
                            board[x + 2][y - 2] = "B"
                            board[x + 3][y - 3] = "B"
                        elif board[x][y] == "r":
                            board[x][y] = "R"
                            board[x + 1][y - 1] = "R"
                            board[x + 2][y - 2] = "R"
                            board[x + 3][y - 3] = "R"
                    return True, board, "in a / diagonal", board[x][y].lower()
        num = 0
        for row in board:
            for column in row:
                if column != " ":
                    num += 1
        if num == (len(board) * len(board[0])):
            return False, board, "Tie"
        return None, None, None

    def get_empty_connect4(self, board):
        """Yields every empty index on the board"""
        for x, _ in enumerate(board):
            y = 0
            while y != 6:
                if board[5 - y][x] == " ":
                    yield 5-y, x
                    break
                else:
                    y += 1

    def minimax_connect4(self, board, depth, isMaximizing):
        """The minimax algorithm for ttt"""
        won = self.has_won_connect4(board, True)
        if depth == 6:
            return 1
        elif won[0] and won[3] == "r":
            return -1
        elif won[0] and won[3] == "b":
            return 1
        elif won[0] == False:
            return 0

        if isMaximizing:
            bestScore = -800
            for x, y in self.get_empty_connect4(board):
                board[x][y] = "b"
                score = self.minimax_connect4(board, depth + 1, False)
                board[x][y] = " "
                if score > bestScore:
                    bestScore = score
        else:
            bestScore = 800
            for x, y in self.get_empty_connect4(board):
                board[x][y] = "r"
                score = self.minimax_connect4(board, depth + 1, True)
                board[x][y] = " "
                if score < bestScore:
                    bestScore = score

        return bestScore

    def make_bot_move_connect4(self, board, difficulty):
        """Returns the best move the bot can take"""
        if difficulty == 1:
            x, y = random.choice(list(self.get_empty_connect4(board)))
            board[x][y] = 'b'
        else:
            bestScore = -800
            bestMove = 0
            for x, y in self.get_empty_connect4(board):
                board[x][y] = "o"
                score = self.minimax_connect4(board, 0, False)
                board[x][y] = " "
                if score > bestScore:
                    bestScore = score
                    bestMove = x, y
            board[bestMove[0]][bestMove[1]] = 'b'

        return board

    @commands.command()
    async def connect4(self, ctx, member: discord.Member = None):
        """a two-player connection board game, in which the players take turns dropping colored discs into a seven-column, six-row vertically suspended grid."""
        if not member:
            board = [[" " for _ in range(7)] for i in range(6)]
            turn = ctx.author
            await ctx.send("Choose ai difficulty, easy/hard:")
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author
                and m.channel == ctx.channel
                and m.content.lower() in ["easy", "hard"],
            )
            difficulty = 1 if msg.content.lower() == "easy" else 2
            e = discord.Embed(
                title="Connect4",
                description=f"How to play: type a number 1-7 to drop a token inside that column\nturn: `{turn.display_name}`\n\n{self.format_connect4_board(board)}",
                color=discord.Color.blurple(),
            ).set_footer(text='Send "end"/"stop"/"cancel" to stop the game')
            msg = await ctx.send(embed=e)
            while True:
                e = discord.Embed(
                    title="Connect4",
                    description=f"How to play: type a number 1-7 to drop a token inside that column\nturn: `{turn.display_name}`\n\n{self.format_connect4_board(board)}",
                    color=discord.Color.blurple(),
                ).set_footer(text='Send "end"/"stop"/"cancel" to stop the game')
                await msg.edit(embed=e)
                if turn == ctx.author:
                    inp = await self.bot.wait_for(
                        "message",
                        check=lambda m: m.author == turn and m.channel == ctx.channel,
                    )
                    if inp.content.lower() in ["stop", "end", "cancel"]:
                        return await ctx.send("Ended the game")
                    if len(inp.content) != 1:
                        continue
                    try:
                        x = int(inp.content) - 1
                    except ValueError:
                        await ctx.send(f"Invalid Syntax: {inp.content} is not a number")
                        continue
                    if x not in range(7):
                        await ctx.send(
                            f"Invalid syntax: {inp.content} isnt a valid place on the board"
                        )
                        continue
                    y = 0
                    while y <= 6:
                        if y == 6:
                            await ctx.send(
                                "Invalid Syntax: Cant add to this column anymore"
                            )
                            break
                        if board[5 - y][x] == " ":
                            board[5 - y][x] = "r" if turn == ctx.author else "b"
                            break
                        else:
                            y += 1
                else:
                    board = self.make_bot_move_connect4(board, difficulty)

                won = self.has_won_connect4(board)
                if won[0]:
                    await ctx.send(f"{turn.mention} connected 4 {won[2]}")
                    e = discord.Embed(
                        title="Connect4",
                        description=self.format_connect4_board(won[1]),
                        color=discord.Color.blurple(),
                    )
                    return await ctx.send(embed=e)
                elif won[0] == False:
                    await ctx.send("Tie")
                    e = discord.Embed(
                        title="Connect4",
                        description=self.format_connect4_board(won[1]),
                        color=discord.Color.blurple(),
                    )
                    return await ctx.send(embed=e)
                turn = self.bot.user if turn == ctx.author else ctx.author
        elif member.bot or member == ctx.author:
            return await ctx.send(
                f"Invalid Syntax: Can't play against {member.display_name}"
            )
        else:
            board = [[" " for _ in range(7)] for i in range(6)]
            e = discord.Embed(
                title="Connect4",
                description=f"How to play: type a number 1-7 to drop a token inside that column\nturn: `{turn.display_name}`\n\n{self.format_connect4_board(board)}",
                color=discord.Color.blurple(),
            ).set_footer(text='Send "end"/"stop"/"cancel" to stop the game')
            msg = await ctx.send(embed=e)
            turn = ctx.author
            while True:
                e = discord.Embed(
                    title="Connect4",
                    description=f"How to play: type a number 1-7 to drop a token inside that column\nturn: `{turn.display_name}`\n\n{self.format_connect4_board(board)}",
                    color=discord.Color.blurple(),
                ).set_footer(text='Send "end"/"stop"/"cancel" to stop the game')
                await msg.edit(embed=e)
                inp = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.author == turn and m.channel == ctx.channel,
                )
                if inp.content.lower() in ["stop", "end", "cancel"]:
                    return await ctx.send("Ended the game")
                if len(inp.content) != 1:
                    continue
                try:
                    x = int(inp.content) - 1
                except ValueError:
                    await ctx.send(f"Invalid Syntax: {inp.content} is not a number")
                    continue
                if x not in range(7):
                    await ctx.send(
                        f"Invalid syntax: {inp.content} isnt a valid place on the board"
                    )
                    continue
                y = 0
                while y <= 6:
                    if y == 6:
                        await ctx.send(
                            "Invalid Syntax: Cant add to this column anymore"
                        )
                        break
                    if board[5 - y][x] == " ":
                        board[5 - y][x] = "r" if turn == ctx.author else "b"
                        break
                    else:
                        y += 1
                won = self.has_won_connect4(board)
                if won[0]:
                    await ctx.send(f"{turn.mention} connected 4 {won[2]}")
                    e = discord.Embed(
                        title="Connect4",
                        description=self.format_connect4_board(won[1]),
                        color=discord.Color.blurple(),
                    )
                    return await ctx.send(embed=e)
                elif won[0] == False:
                    await ctx.send("Tie")
                    e = discord.Embed(
                        title="Connect4",
                        description=self.format_connect4_board(won[1]),
                        color=discord.Color.blurple(),
                    )
                    return await ctx.send(embed=e)
                turn = member if turn == ctx.author else ctx.author
