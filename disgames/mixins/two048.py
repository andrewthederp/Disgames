import random, discord
from discord.ext import commands


class _2048(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def format_2048_board(self, board):
        """Format the 2048 board"""
        h = ["".join(str(row)) for row in board]
        h = "\n".join(h)
        return f"```\n{h}\n```"

    def go_up(self, board):
        """Move all the numbers on the board upwards"""
        moved = False
        for x in range(4):
            for y in range(4):
                if board[y][x] != 0 and y < 3:
                    for yprime in range(y + 1, 4):
                        if board[yprime][x] != 0:
                            if board[yprime][x] == board[y][x]:
                                board[y][x] = 2 * board[y][x]
                                moved = True
                                board[yprime][x] = 0
                            break
            for y in range(4):
                if board[y][x] == 0 and y < 3:
                    for yprime in range(y + 1, 4):
                        if board[yprime][x] != 0:
                            board[y][x] = board[yprime][x]
                            board[yprime][x] = 0
                            moved = True
                            break
        return moved, board

    def go_down(self, board):
        """Move all the numbers on the board downwards"""
        moved = False
        for x in range(4):
            for y in range(3, -1, -1):
                if board[y][x] != 0 and y > 0:
                    for yprime in range(y - 1, -1, -1):
                        if board[yprime][x] != 0:
                            if board[yprime][x] == board[y][x]:
                                board[y][x] = board[y][x] * 2
                                moved = True
                                board[yprime][x] = 0
                            break
            for y in range(3, -1, -1):
                if board[y][x] == 0 and y > 0:
                    for yprime in range(y - 1, -1, -1):
                        if board[yprime][x] != 0:
                            board[y][x] = board[yprime][x]
                            board[yprime][x] = 0
                            moved = True
                            break
        return moved, board

    def go_right(self, board):
        """Move all the numbers on the board right"""
        moved = False
        for y in range(4):
            for x in range(3, -1, -1):
                if board[y][x] != 0 and x > 0:
                    for xprime in range(x - 1, -1, -1):
                        if board[y][xprime] != 0:
                            if board[y][xprime] == board[y][x]:
                                board[y][x] = 2 * board[y][x]
                                moved = True
                                board[y][xprime] = 0
                            break
            for x in range(3, -1, -1):
                if board[y][x] == 0 and x > 0:
                    for xprime in range(x - 1, -1, -1):
                        if board[y][xprime] != 0:
                            board[y][x] = board[y][xprime]
                            board[y][xprime] = 0
                            moved = True
                            break
        return moved, board

    def go_left(self, board):
        """Move all the numbers on the board left"""
        moved = False
        for y in range(4):
            for x in range(4):
                if board[y][x] != 0 and x < 3:
                    for xprime in range(x + 1, 4):
                        if board[y][xprime] != 0:
                            if board[y][x] == board[y][xprime]:
                                board[y][x] = 2 * board[y][x]
                                moved = True
                                board[y][xprime] = 0
                            break
            for x in range(4):
                if board[y][x] == 0 and x < 3:
                    for xprime in range(x + 1, 4):
                        if board[y][xprime] != 0:
                            board[y][x] = board[y][xprime]
                            board[y][xprime] = 0
                            moved = True
                            break
        return moved, board

    def add_number(self, board):
        """Add either a 2 or 4 onto the board"""

        while True:
            x = random.randint(0, 3)
            y = random.randint(0, 3)

            pickanumber = random.randint(0, 9)
            num = 4 if pickanumber < 1 else 2
            if board[x][y] == 0:
                board[x][y] = num
                break
        return board

    def get_result(self, board):
        """Check if the game is over"""
        zeroes = 0
        playsleft = False
        for x in range(len(board)):
            for y in range(len(board[x])):
                if board[x][y] == 2048:
                    return True
        for y in range(4):
            zeroes += board[y].count(0)
            if zeroes > 0:
                break
            for x in range(4):
                if x < 3 and board[y][x + 1] == board[y][x]:
                    playsleft = True
                    break
                if y < 3 and board[y + 1][x] == board[y][x]:
                    playsleft = True
                    break
            if playsleft:
                break

        if zeroes == 0 and not playsleft:
            return False

    def create_2048_board(self):
        b = [[0 for _ in range(4)] for _ in range(4)]
        b = self.add_number(b)
        b = self.add_number(b)
        return b

    @commands.command("2048")
    async def _2048_(self, ctx):
        """you combine like-numbered tiles numbered with powers of two until you get a tile with the value of 2048. Gameplay consists of swiping the tiles up, right, down and left, and any tiles that match in the direction and adjacent spot will combine in the direction swiped."""
        b = self.create_2048_board()
        e = discord.Embed(
            title="2048",
            description=self.format_2048_board(b),
            color=discord.Color.blurple(),
        ).set_footer(text='React with "⏹️" to end the game')
        msg = await ctx.send(embed=e)
        for emoji in ["➡️", "⬆️", "⏹️", "⬇️", "⬅️"]:
            await msg.add_reaction(emoji)
        while True:
            e = discord.Embed(
                title="2048",
                description=self.format_2048_board(b),
                color=discord.Color.blurple(),
            ).set_footer(text='React with "⏹️" to end the game')
            await msg.edit(embed=e)
            reaction, user = await self.bot.wait_for(
                "reaction_add",
                check=lambda r, u: u == ctx.author
                and r.message == msg
                and str(r) in ["⬆️", "➡️", "⏹️", "⬅️", "⬇️"],
            )
            try:
                await msg.remove_reaction(str(reaction), user)
            except discord.Forbidden:
                pass
            if str(reaction) == "⏹️":
                await ctx.send("Game ended")
                return
            elif str(reaction) == "⬆️":
                ans, b = self.go_up(b)
            elif str(reaction) == "⬇️":
                ans, b = self.go_down(b)
            elif str(reaction) == "➡️":
                ans, b = self.go_right(b)
            elif str(reaction) == "⬅️":
                ans, b = self.go_left(b)
            if ans:
                b = self.add_number(b)
            res = self.get_result(b)
            if res:
                e = discord.Embed(
                    title="2048",
                    description=self.format_2048_board(b),
                    color=discord.Color.blurple(),
                )
                await msg.edit(content="You won!!!", embed=e)
                return
            elif res == False:
                e = discord.Embed(
                    title="2048",
                    description=self.format_2048_board(b),
                    color=discord.Color.blurple(),
                )
                await msg.edit(content="You lost", embed=e)
                return
