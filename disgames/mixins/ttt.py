import discord
from discord.ext import commands
import random


class TicTacToe(commands.Cog):
    """
    Tic Tac Toe command
    """

    def __init__(self, bot):
        self.bot = bot

    def format_ttt_board(self, board):
        """Format the ttt board"""
        lst = ["  1 2 3"]
        for x, row in enumerate(board, start=1):
            lst.append("".join([str(x) + "|" + "|".join(row)]))
        return "\n".join(lst)

    def get_empty_ttt(self, board):
        """Yields every empty index on the board"""
        for x, row in enumerate(board):
            for y, column in enumerate(row):
                if column == " ":
                    yield x, y

    def minimax_ttt(self, board, depth, isMaximizing):
        """The minimax algorithm for ttt"""
        won = self.has_won_ttt(board)
        if won[0] and won[1] == "x":
            return -1
        elif won[0] and won[1] == "o":
            return 1
        elif won[0] == False:
            return 0

        if isMaximizing:
            bestScore = -800
            for x, y in self.get_empty_ttt(board):
                board[x][y] = "o"
                score = self.minimax_ttt(board, depth + 1, False)
                board[x][y] = " "
                if score > bestScore:
                    bestScore = score
        else:
            bestScore = 800
            for x, y in self.get_empty_ttt(board):
                board[x][y] = "x"
                score = self.minimax_ttt(board, depth + 1, True)
                board[x][y] = " "
                if score < bestScore:
                    bestScore = score

        return bestScore

    def make_bot_move_ttt(self, board, difficulty):
        """Returns the best move the bot can take"""
        if difficulty == 1:
            return random.choice(
                [str(x) + str(y) for x, y in self.get_empty_ttt(board)]
            )
        bestScore = -800
        bestMove = 0
        for x, y in self.get_empty_ttt(board):
            board[x][y] = "o"
            score = self.minimax_ttt(board, 0, False)
            board[x][y] = " "
            if score > bestScore:
                bestScore = score
                bestMove = str(x), str(y)
        return bestMove

    def make_ttt_move(self, move, board, turn):
        """Checks if `move` is a valid move or not"""
        if move not in [
            "11",
            "12",
            "13",
            "21",
            "22",
            "23",
            "31",
            "32",
            "33",
        ]:
            return (
                False,
                f"Invalid Syntax: {move} isn't a valid place on the board, Please try again",
            )
        if board[int(move[0]) - 1][int(move[1]) - 1] != " ":
            return (
                False,
                f"Invalid Syntax: {move} has already been chosen, Please try again",
            )
        board[int(move[0]) - 1][int(move[1]) - 1] = turn
        return True, board

    def has_won_ttt(self, board):
        """Checks if someone won, returns True and the winner if someone won, returns False and "tie" if it was a tie"""
        BLANK = " "
        for i in range(3):

            if (board[i][0] == board[i][1] == board[i][2]) and board[i][0] != BLANK:
                return (True, board[i][0])
            if (board[0][i] == board[1][i] == board[2][i]) and board[0][i] != BLANK:
                return (True, board[0][i])

        if (board[0][0] == board[1][1] == board[2][2]) and board[0][0] != BLANK:
            return (True, board[0][0])

        if (board[0][2] == board[1][1] == board[2][0]) and board[0][2] != BLANK:
            return (True, board[0][2])
        if sum(i.count(BLANK) for i in board) == 0:
            return (False, "tie")
        return (None, "h")

    @commands.command(aliases=["ttt"])
    async def tictactoe(self, ctx: commands.Context, member: discord.Member = None):
        """two players take turns marking the spaces in a three-by-three grid with X or O. The player who succeeds in placing three of their marks in a horizontal, vertical, or diagonal row is the winner"""
        if member is None:
            turn = ctx.author
            board = [[" " for i in range(3)] for i in range(3)]
            await ctx.send("Choose ai difficulty, easy/hard:")
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author
                and m.channel == ctx.channel
                and m.content.lower() in ["easy", "hard"],
            )
            difficulty = 1 if msg.content.lower() == "easy" else 2
            embed = discord.Embed(
                title="TicTacToe",
                description=f"How to play: send the coordinates of where you want to place your token, eg: `22`\n\nturn: `{turn.display_name}`\n```\n{self.format_ttt_board(board)}\n```",
                color=discord.Color.blurple(),
            ).set_footer(text='Send "end"/"stop"/"cancel" to stop the game')
            msg = await ctx.send(embed=embed)
            while True:
                if turn == ctx.author:
                    inp = await ctx.bot.wait_for(
                        "message",
                        check=lambda m: m.author == turn and m.channel == ctx.channel,
                    )
                    if inp.content.lower() in ["cancel", "end", "stop"]:
                        return await ctx.send("Cancelled the game")
                    outp = self.make_ttt_move(inp.content, board, "x")
                    if outp[0]:
                        board = outp[1]
                    else:
                        await ctx.send(outp[1], delete_after=5)
                        continue
                else:
                    move = self.make_bot_move_ttt(board, difficulty)
                    board[int(move[0])][int(move[1])] = "o"
                h = self.has_won_ttt(board)
                if h[0]:
                    return await ctx.send(
                        embed=discord.Embed(
                            color=discord.Color.blurple(),
                            title="TicTacToe",
                            description=(
                                "winner: `"
                                f"{turn.display_name}`"
                                "\n"
                                f"```\n{self.format_ttt_board(board)}```"
                                "\n"
                            ),
                        )
                    )
                elif h[0] == False:
                    return await ctx.send(
                        embed=discord.Embed(
                            color=discord.Color.blurple(),
                            title="TicTacToe",
                            description=(
                                "winner: `"
                                "Tie`"
                                "\n"
                                f"```\n{self.format_ttt_board(board)}```"
                                "\n"
                            ),
                        )
                    )
                turn = ctx.bot.user if turn == ctx.author else ctx.author
                await msg.edit(
                    embed=discord.Embed(
                        title="TicTacToe",
                        description=f"How to play: send the coordinates of where you want to place your token, eg: `22`\n\nturn: `{turn.display_name}`\n```\n{self.format_ttt_board(board)}\n```",
                        color=discord.Color.blurple(),
                    ).set_footer(text='Send "end"/"stop"/"cancel" to stop the game')
                )
        elif member.bot or member == ctx.author:
            return await ctx.send(
                f"Invalid Syntax: Can't play against {member.display_name}"
            )
        else:
            turn = ctx.author
            board = [[" " for i in range(3)] for i in range(3)]
            embed = discord.Embed(
                title="TicTacToe",
                description=f"How to play: send the coordinates of where you want to place your token, eg: `22`\n\nturn: `{turn.display_name}`\n```\n{self.format_ttt_board(board)}\n```",
                color=discord.Color.blurple(),
            ).set_footer(text='Send "end"/"stop"/"cancel" to stop the game')
            msg = await ctx.send(embed=embed)
            while True:
                inp = await ctx.bot.wait_for(
                    "message",
                    check=lambda m: m.author == turn and m.channel == ctx.channel,
                )
                if inp.content in ["cancel", "end", "stop"]:
                    return await ctx.send("Cancelled the game")
                outp = self.make_ttt_move(
                    inp.content, board, "x" if turn == ctx.author else "o"
                )
                if outp[0]:
                    board = outp[1]
                else:
                    await ctx.send(outp[1])
                    continue
                h = self.has_won_ttt(board)
                if h[0]:
                    return await ctx.send(
                        embed=discord.Embed(
                            title="TicTacToe",
                            color=discord.Color.blurple(),
                            description=(
                                "winner: `"
                                f"{turn.display_name}`"
                                "\n"
                                f"```\n{self.format_ttt_board(board)}```"
                                "\n"
                            ),
                        ).set_footer(text='Send "end"/"stop"/"cancel" to stop the game')
                    )
                elif h[0] == False:
                    return await ctx.send(
                        embed=discord.Embed(
                            title="TicTacToe",
                            color=discord.Color.blurple(),
                            description=(
                                "winner: `"
                                f"Tie`"
                                "\n"
                                f"```\n{self.format_ttt_board(board)}```"
                                "\n"
                            ),
                        ).set_footer(text='Send "end"/"stop"/"cancel" to stop the game')
                    )
                turn = member if turn == ctx.author else ctx.author
                await msg.edit(
                    embed=discord.Embed(
                        title="TicTacToe",
                        description=f"How to play: send the coordinates of where you want to place your token, eg: `22`\n\nturn: `{turn.display_name}`\n```\n{self.format_ttt_board(board)}\n```",
                        color=discord.Color.blurple(),
                    ).set_footer(text='Send "end"/"stop"/"cancel" to stop the game')
                )
