import discord
from discord.ext import commands
import chess
import os
from stockfish import Stockfish
from pathlib import Path

class PathNeeded(Exception):
    pass

class Chess(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            h = os.getcwd().split('\\')[2]
        except IndexError:
            self.stockfish_path = None
        else:
            self.stockfish_path = sorted(Path(f"C:\\Users\\{h}").rglob("stockfish_20011801_32bit.exe"))

    def create_chess_board(self, board, turn, member):
        fen = board.fen().split(" ")[0]
        url = f"http://www.fen-to-image.com/image/64/double/coords/{fen}"
        e = discord.Embed(
            title="Chess",
            description="To move a piece get it's current coordinates and the coordinates of where it needs to be, eg: `a2a4`\nto end the game type `stop`\nto go back once type `back`",
            color=discord.Color.blurple(),
        )
        e.add_field(name="Turn", value=turn.mention, inline=False)
        e.add_field(
            name=f"Legal moves",
            value=", ".join([f"`{str(i)}`" for i in board.legal_moves]),
            inline=False,
        )
        e.add_field(name="Check", value=board.is_check(), inline=False)
        if board.halfmove_clock >= 45:
            e.add_field(name="Half move clock", value=board.halfmove_clock)
        value = None
        if board.is_stalemate():
            value = "Tie - Stalemate"
        elif board.is_insufficient_material():
            value = "Tie - Insufficient Materials"
        elif board.can_claim_threefold_repetition():
            value = "Tie - Threefold repetition"
        elif board.can_claim_fifty_moves():
            value = "Tie - Fifty move rule"
        elif board.is_check() and not board.legal_moves:
            value = f"{member.mention} - CheckMate"
        if value:
            e.description = "GAME OVER"
            e.add_field(name="Winner", value=value)
        e.set_image(url=url)
        return e

    def get_best_move(self, board, smort_level):
        if not self.stockfish_path:
            raise PathNeeded("Couldn't find the path to your stockfish_20011801_32bit.exe")
        stockfish = Stockfish(str(self.stockfish_path[0]), parameters={'Skill Level':smort_level})
        stockfish.set_fen_position(board.fen())
        return stockfish.get_best_move()

    @commands.command("chess")
    async def chess(self, ctx, member: discord.Member=None):
        if member == None:
            await ctx.send("Please enter a a difficulty level from 0-20")
            smort_level = await self.bot.wait_for('message', check=lambda m:m.author == ctx.author and m.channel == ctx.channel)
            try:
                smort_level = int(smort_level.content)
            except ValueError:
                return await ctx.send("That's not a number")
            else:
                if smort_level not in range(21):
                    return await ctx.send("difficulty needs to be in 0-20")
            board = chess.Board()
            turn = ctx.author
            e = self.create_chess_board(board, turn, member if turn == ctx.author else ctx.author)
            msg = await ctx.send(embed=e)
            while True:
                if turn == ctx.author:
                    inp = await self.bot.wait_for(
                        "message",
                        check=lambda m: m.author == ctx.author
                        and m.channel == ctx.channel,
                    )
                    if inp.content.lower() in ["stop","cancel","end"]:
                        return await ctx.send("Game ended", delete_after=5)
                    elif inp.content.lower() == "back":
                        try:
                            board.pop()
                        except IndexError:
                            await ctx.send("Can't go back", delete_after=5)
                            continue
                    else:
                        try:
                            move = chess.Move.from_uci(inp.content)
                            board.push(move)
                        except ValueError:
                            await ctx.send("Invalid move", delete_after=5)
                            continue
                        try:
                            await inp.delete()
                        except discord.Forbidden:
                            pass
                else:
                    move = self.get_best_move(board, smort_level)
                    move = chess.Move.from_uci(str(move))
                    board.push(move)
                turn = ctx.bot.user if turn == ctx.author else ctx.author
                e = self.create_chess_board(board, turn, ctx.bot.user if turn == ctx.author else ctx.author)
                await msg.edit(embed=e)
        else:
            if member.bot or member == ctx.author:
                return await ctx.send(
                    f"Invalid Syntax: Can't play against {member.display_name}"
                )
            board = chess.Board()
            turn = ctx.author
            e = self.create_chess_board(board, turn, member if turn == ctx.author else ctx.author)
            msg = await ctx.send(embed=e)
            while True:
                inp = await ctx.bot.wait_for(
                    "message",
                    check=lambda m: m.author in [ctx.author, member]
                    and m.channel == ctx.channel,
                )
                if inp.content.lower() == "stop":
                    return await ctx.send("Game ended", delete_after=5)
                elif inp.content.lower() == "back":
                    try:
                        board.pop()
                    except IndexError:
                        await ctx.send("Can't go back", delete_after=5)
                        continue
                else:
                    if inp.author == turn:
                        try:
                            move = chess.Move.from_uci(inp.content)
                            board.push(move)
                        except ValueError:
                            await ctx.send("Invalid move", delete_after=5)
                            continue
                        try:
                            await inp.delete()
                        except discord.Forbidden:
                            pass
                turn = member if turn == ctx.author else ctx.author
                e = self.create_chess_board(board, turn, member if turn == ctx.author else ctx.author)
                await msg.edit(embed=e)
