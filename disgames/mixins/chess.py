import discord
from discord.ext import commands
import chess


class Chess(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_chess_board(self, board, turn):
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
            value = f"{turn.mention} - CheckMate"
        if value:
            e.description = "GAME OVER"
            e.add_field(name="Winner", value=value)
        e.set_image(url=url)
        return e

    def evaluation(self, board):
        i = 0
        evaluation = 0
        x = True
        try:
            x = bool(board.piece_at(i).color)
        except AttributeError as e:
            x = x
        while i < 63:
            i += 1
            evaluation = evaluation + (
                self.getPieceValue(str(board.piece_at(i)))
                if x
                else -self.getPieceValue(str(board.piece_at(i)))
            )
        return evaluation

    def minimax(self, depth, board, alpha, beta, is_maximizing):
        if depth == 0:
            return -self.evaluation(board)
        possibleMoves = board.legal_moves
        if is_maximizing:
            bestMove = -9999
            for x in possibleMoves:
                move = chess.Move.from_uci(str(x))
                board.push(move)
                bestMove = max(
                    bestMove,
                    self.minimax(depth - 1, board, alpha, beta, not is_maximizing),
                )
                board.pop()
                alpha = max(alpha, bestMove)
                if beta <= alpha:
                    return bestMove
            return bestMove
        else:
            bestMove = 9999
            for x in possibleMoves:
                move = chess.Move.from_uci(str(x))
                board.push(move)
                bestMove = min(
                    bestMove,
                    self.minimax(depth - 1, board, alpha, beta, not is_maximizing),
                )
                board.pop()
                beta = min(beta, bestMove)
                if beta <= alpha:
                    return bestMove
            return bestMove

    def minimaxRoot(self, depth, board, isMaximizing):
        possibleMoves = board.legal_moves
        bestMove = -9999
        bestMoveFinal = None
        for x in possibleMoves:
            move = chess.Move.from_uci(str(x))
            board.push(move)
            value = max(
                bestMove,
                self.minimax(depth - 1, board, -10000, 10000, not isMaximizing),
            )
            board.pop()
            if value > bestMove:
                bestMove = value
                bestMoveFinal = move
        return bestMoveFinal

    def getPieceValue(self, piece):
        if piece == None:
            return 0
        if piece == "P" or piece == "p":
            return 10
        if piece == "N" or piece == "n":
            return 30
        if piece == "B" or piece == "b":
            return 30
        if piece == "R" or piece == "r":
            return 50
        if piece == "Q" or piece == "q":
            return 90
        if piece == "K" or piece == "k":
            return 900
        return 0

    @commands.command("chess")
    async def command(self, ctx, member: discord.Member = None):
        if member == None:
            board = chess.Board()
            turn = ctx.author
            e = self.create_chess_board(board, turn)
            msg = await ctx.send(embed=e)
            while True:
                if turn == ctx.author:
                    inp = await bot.wait_for(
                        "message",
                        check=lambda m: m.author == ctx.author
                        and m.channel == ctx.channel,
                    )
                    if inp.content.lower() == "stop":
                        return await ctx.send("Game ended", delete_after=10)
                    elif inp.content.lower() == "back":
                        try:
                            board.pop()
                        except IndexError:
                            await ctx.send("Can't go back", delete_after=10)
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
                    move = self.minimaxRoot(3, board, True)
                    move = chess.Move.from_uci(str(move))
                    board.push(move)
                e = self.create_chess_board(board, turn)
                await msg.edit(embed=e)
                turn = ctx.bot.user if turn == ctx.author else ctx.author
        else:
            if member.bot or member == ctx.author:
                return await ctx.send(
                    f"Invalid Syntax: Can't play against {member.display_name}"
                )
            board = chess.Board()
            turn = ctx.author
            e = self.create_chess_board(board, turn)
            msg = await ctx.send(embed=e)
            while True:
                inp = await ctx.bot.wait_for(
                    "message",
                    check=lambda m: m.author in [ctx.author, member]
                    and m.channel == ctx.channel,
                )
                if inp.content.lower() == "stop":
                    return await ctx.send("Game ended", delete_after=10)
                elif inp.content.lower() == "back":
                    try:
                        board.pop()
                    except IndexError:
                        await ctx.send("Can't go back", delete_after=10)
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
                e = self.create_chess_board(board, turn)
                await msg.edit(embed=e)
                turn = member if turn == ctx.author else ctx.author
