import discord
from discord.ext import commands
import chess
import os
from stockfish import Stockfish
from pathlib import Path
from ..errors import PathNotFound


class Chess(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stockfish_path = None
        try:
            path = os.getcwd().split("\\")[2]
        except IndexError:
            pass
        else:
            stockfish_path = sorted(
                Path(f"C:\\Users\\{path}").rglob("stockfish_20011801_32bit.exe")
            )
            if stockfish_path:
                self.stockfish_path = stockfish_path[0]

    def has_won_chess(self, board, member):
        """Checks if game is over"""
        value = None
        results = board.result()
        if board.is_checkmate():
            value = f"Checkmate, Winner: {member.mention} | Score: `{results}`"
        elif board.is_stalemate():
            value = f"Stalemate | Score: `{results}`"
        elif board.is_insufficient_material():
            value = (
                f"Insufficient material left to continue the game | Score: `{results}`"
            )
        elif board.is_seventyfive_moves():
            value = f"75-moves rule | Score: `{results}`"
        elif board.is_fivefold_repetition():
            value = f"Five-fold repitition. | Score: `{results}`"
        return value

    def create_chess_board(self, board, turn, member):
        """Creates the chess embed"""
        url = f"http://www.fen-to-image.com/image/64/double/coords/{board.board_fen()}"
        e = discord.Embed(
            title="Chess",
            description="To move a piece get it's current coordinates and the coordinates of where you want it to be, eg: `a2a4`",
            color=discord.Color.blurple(),
        )
        e.add_field(name="Turn", value=turn.mention, inline=False)
        e.add_field(
            name=f"Legal moves",
            value=", ".join([f"`{str(i)}`" for i in board.legal_moves]) or 'No legal moves',
            inline=False,
        )
        e.add_field(name="Check", value=board.is_check(), inline=False)
        if board.halfmove_clock >= 45:
            e.add_field(name="Half move clock", value=board.halfmove_clock)
        gameOver = self.has_won_chess(board, member)
        if gameOver:
            e.description = "GAME OVER"
            e.add_field(name="Winner", value=gameOver)
        e.set_image(url=url)
        e.set_footer(
            text='Send "end"/"stop"/"cancel" to stop the game | "back" to go back a step | "re"/"re-send"/"resend" to send a new embed'
        )
        return e

    def get_best_chess_move(self, stockfish, board):
        """Gets the best move using the stockfish_20011801_32bit.exe"""
        stockfish.set_fen_position(board.fen())
        return stockfish.get_best_move()

    @commands.command("chess")
    async def chess(self, ctx, member: discord.Member = None):
        """a board game of strategic skill for two players, played on a chequered board on which each playing piece is moved according to precise rules. The object is to put the opponent's king under a direct attack from which escape is impossible"""
        if member == None:
            if not self.stockfish_path:
                raise PathNotFound
            await ctx.send("Please enter a a difficulty level from 0-20")
            smort_level = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
            )
            try:
                smort_level = int(smort_level.content)
            except ValueError:
                return await ctx.send("That's not a number")
            else:
                if smort_level not in range(21):
                    return await ctx.send("difficulty needs to be in 0-20")
            try:
                stockfish = Stockfish(
                    str(self.stockfish_path), parameters={"Skill Level": smort_level}
                )
            except (AttributeError, FileNotFoundError):
                raise PathNotFound

            board = chess.Board()
            turn = ctx.author
            e = self.create_chess_board(
                board, turn, member if turn == ctx.author else ctx.author
            )
            msg = await ctx.send(embed=e)
            while True:
                if turn == ctx.author:
                    def check(m):
                        try:
                            if board.parse_uci(m.content.lower()):
                                return m.author == turn and m.channel == ctx.channel
                            else:
                                return False
                        except ValueError:
                            return m.content.lower() in ['end','stop','cancel','re','re-send','resend','back']
                    inp = await self.bot.wait_for("message",check=check)
                    if inp.content.lower() in ["stop", "cancel", "end"]:
                        return await ctx.send("Game ended", delete_after=5)
                    elif inp.content.lower() == "back":
                        try:
                            board.pop()
                            turn = member if turn == ctx.author else ctx.author
                            continue
                        except IndexError:
                            await ctx.send("Can't go back", delete_after=5)
                            continue
                    elif inp.content.lower() in ['re','re-send','resend']:
                        e = self.create_chess_board(board, turn, member if turn == ctx.author else ctx.author)
                        msg = await ctx.send(embed=e)
                        continue
                    else:
                        board.push_uci(inp.content.lower())
                        try:
                            await inp.delete()
                        except discord.Forbidden:
                            pass
                else:
                    move = self.get_best_chess_move(stockfish, board)
                    move = chess.Move.from_uci(str(move))
                    board.push(move)
                turn = ctx.bot.user if turn == ctx.author else ctx.author
                won = self.has_won_chess(
                    board, ctx.bot.user if turn == ctx.author else ctx.author
                )
                if won:
                    e = self.create_chess_board(
                        board, turn, ctx.bot.user if turn == ctx.author else ctx.author
                    )
                    return await ctx.send(embed=e)
                e = self.create_chess_board(
                    board, turn, ctx.bot.user if turn == ctx.author else ctx.author
                )
                await msg.edit(embed=e)
        elif member.bot or member == ctx.author:
            return await ctx.send(
                f"Invalid Syntax: Can't play against {member.display_name}"
            )
        else:
            board = chess.Board()
            turn = ctx.author
            e = self.create_chess_board(
                board, turn, member if turn == ctx.author else ctx.author
            )
            msg = await ctx.send(embed=e)
            while True:
                def check(m):
                    try:
                        if board.parse_uci(m.content.lower()) or m.content.lower() in ['end','stop','cancel','re','re-send','resend','back']:
                            return m.author == turn and m.channel == ctx.channel
                        else:
                            return False
                    except ValueError:
                        return m.content.lower() in ['end','stop','cancel','re','re-send','resend','back']
                inp = await ctx.bot.wait_for(
                    "message",
                    check=check
                )
                if inp.content.lower() in ["stop", "end", "cancel"]:
                    return await ctx.send("Game ended", delete_after=5)
                elif inp.content.lower() == "back":
                    try:
                        board.pop()
                    except IndexError:
                        await ctx.send("Can't go back", delete_after=5)
                        continue
                elif inp.content.lower() in ['re','re-send','resend']:
                    e = self.create_chess_board(board, turn, member if turn == ctx.author else ctx.author)
                    msg = await ctx.send(embed=e)
                    continue
                else:
                    if inp.author == turn:
                        board.push_uci(inp.content.lower())
                        try:
                            await inp.delete()
                        except discord.Forbidden:
                            pass
                    else:
                        continue
                turn = member if turn == ctx.author else ctx.author
                won = self.has_won_chess(
                    board, member if turn == ctx.author else ctx.author
                )
                if won:
                    e = self.create_chess_board(
                        board, turn, member if turn == ctx.author else ctx.author
                    )
                    return await ctx.send(embed=e)
                e = self.create_chess_board(
                    board, turn, member if turn == ctx.author else ctx.author
                )
                await msg.edit(embed=e)
