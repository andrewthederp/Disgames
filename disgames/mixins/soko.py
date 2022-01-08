import random, copy, discord
from discord.ext import commands


class Sokoban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def format_soko_board(self, board):
        """Format the soko board"""
        dct = {
            "p": ":flushed:",
            " ": random.choice(
                [
                    ":purple_square:",
                    ":black_large_square:",
                    ":green_square:",
                    ":yellow_square:",
                    ":blue_square:",
                ]
            ),
            "tp": ":flushed:",
            "tb": ":white_check_mark:",
            "t": ":x:",
            "b": ":brown_square:",
        }
        lst = []
        for i in board:
            scn_lst = []
            for thing in i:
                scn_lst.append(dct[thing])
            lst.append("".join(scn_lst))
        return "\n".join(lst)

    def create_soko_board(self, difficulty_level):
        """Creates the soko board based on the difficulty level"""
        num1 = 8 - difficulty_level // 4
        num2 = 8 - difficulty_level // 4
        if num1 >= 5:
            num1 = random.randint(5, 9)
            num2 = random.randint(5, 9)
        num3 = 1 + difficulty_level // 5
        if num3 > 7:
            num3 = 7
        board = [[" " for i in range(num1)] for i in range(num2)]
        x, y = random.randint(0, len(board) - 1), random.randint(0, len(board[0]) - 1)
        board[x][y] = "p"
        for _ in range(num3):
            for i in ["t", "b"]:
                if i == "b":
                    x, y = random.randint(1, len(board) - 2), random.randint(
                        1, len(board[0]) - 2
                    )
                else:
                    x, y = random.randint(0, len(board) - 1), random.randint(
                        0, len(board[0]) - 1
                    )
                while board[x][y] != " ":
                    if i == "b":
                        x, y = random.randint(1, len(board) - 2), random.randint(
                            1, len(board[0]) - 2
                        )
                    else:
                        x, y = random.randint(0, len(board) - 1), random.randint(
                            0, len(board[0]) - 1
                        )
                board[x][y] = i
        return board

    def get_player(self, board):
        """Returnes the x,y coordinates of the player"""
        for x, i in enumerate(board):
            for y, thing in enumerate(i):
                if thing == "p" or thing == "tp":
                    return x, y

    def has_won_soko(self, board):
        """Checks if there are no more t on the board"""
        for x in board:
            for y in x:
                if y == "t" or y == "tp":
                    return False
        return True

    @commands.command(aliases=["soko"])
    async def sokoban(self, ctx):
        """the player pushes boxes around the board, trying to get them to :x:"""
        diff_level = 0
        directions = directions = {
            "⬆️": "up",
            "⬅️": "left",
            "➡️": "right",
            "⬇️": "down",
            "🔄": "reset",
            "⏹️": "end",
        }
        msg = await ctx.send("Setting up the game")
        while True:
            board = self.create_soko_board(diff_level)
            origin_board = copy.deepcopy(board)
            em = discord.Embed(
                title="Sokoban",
                description=self.format_soko_board(board),
                color=discord.Color.blurple(),
            ).set_footer(
                text='React with "⏹️" to end the game | React with "🔄" to restart the level'
            )
            em.add_field(
                name="Play",
                value=f"Score: {diff_level}\nReact with a direction (up :arrow_up:, down :arrow_down:, right :arrow_right:, left :arrow_left:)",
            )
            await msg.edit(embed=em)
            for i in ["⬆️", "⬇️", "➡️", "⬅️", "🔄", "⏹️"]:
                await msg.add_reaction(i)
            while True:
                reaction, user = await self.bot.wait_for(
                    "reaction_add",
                    check=lambda r, u: u == ctx.author
                    and r.message == msg
                    and str(r) in ["⬆️", "⬇️", "➡️", "⬅️", "🔄", "⏹️"],
                )
                try:
                    await msg.remove_reaction(str(reaction), user)
                except discord.Forbidden:
                    pass
                inp = directions[str(reaction)]
                if inp == "end":
                    await ctx.send("Ended the game")
                    return
                if inp == "up":
                    try:
                        num = self.get_player(board)
                        if (num[0] - 1) < 0:
                            await ctx.send("Cant go up any further", delete_after=5)
                            continue
                        elif board[num[0] - 1][num[1]] == "b":
                            if (num[0] - 2) < 0:
                                await ctx.send(
                                    "Cant push this box up any further", delete_after=5
                                )
                                continue
                            if board[num[0] - 2][num[1]] == "b":
                                await ctx.send(
                                    "Can't push a 2 boxes at the same time",
                                    delete_after=5,
                                )
                                continue
                            if board[num[0] - 2][num[1]] == "t":
                                board[num[0] - 2][num[1]] = "tb"
                            else:
                                board[num[0] - 2][num[1]] = "b"
                            board[num[0]][num[1]] = " "
                            board[num[0] - 1][num[1]] = "p"
                        elif board[num[0] - 1][num[1]] == "tb":
                            if (num[0] - 2) < 0:
                                await ctx.send(
                                    "Cant push this box up any further", delete_after=5
                                )
                                continue
                            if board[num[0] - 2][num[1]] == "b":
                                await ctx.send(
                                    "Can't push a 2 boxes at the same time",
                                    delete_after=5,
                                )
                                continue
                            if board[num[0] - 2][num[1]] == "t":
                                board[num[0] - 2][num[1]] = "tb"
                            else:
                                board[num[0] - 2][num[1]] = "b"
                            board[num[0]][num[1]] = " "
                            board[num[0] - 1][num[1]] = "tp"
                        else:
                            if board[num[0]][num[1]] == "p":
                                board[num[0]][num[1]] = " "
                            else:
                                board[num[0]][num[1]] = "t"
                            if board[num[0] - 1][num[1]] == "t":
                                board[num[0] - 1][num[1]] = "tp"
                            else:
                                board[num[0] - 1][num[1]] = "p"
                    except IndexError:
                        await ctx.send("Cant do that", delete_after=5)
                        continue
                elif inp == "down":
                    try:
                        num = self.get_player(board)
                        if (num[0] + 1) > len(board) - 1:
                            await ctx.send("Cant go down any further", delete_after=5)
                            continue
                        elif board[num[0] + 1][num[1]] == "b":
                            if (num[0] + 2) > len(board) - 1:
                                await ctx.send(
                                    "Cant push this box down any further",
                                    delete_after=5,
                                )
                                continue
                            if board[num[0] + 2][num[1]] == "b":
                                await ctx.send(
                                    "Can't push a 2 boxes at the same time",
                                    delete_after=5,
                                )
                                continue
                            if board[num[0] + 2][num[1]] == "t":
                                board[num[0] + 2][num[1]] = "tb"
                            else:
                                board[num[0] + 2][num[1]] = "b"
                            board[num[0]][num[1]] = " "
                            board[num[0] + 1][num[1]] = "p"
                        elif board[num[0] + 1][num[1]] == "tb":
                            if (num[0] + 2) < 0:
                                await ctx.send(
                                    "Cant push this box down any further",
                                    delete_after=5,
                                )
                                continue
                            if board[num[0] + 2][num[1]] == "b":
                                await ctx.send(
                                    "Can't push a 2 boxes at the same time",
                                    delete_after=5,
                                )
                                continue
                            if board[num[0] + 2][num[1]] == "t":
                                board[num[0] + 2][num[1]] = "tb"
                            else:
                                board[num[0] + 2][num[1]] = "b"
                            board[num[0]][num[1]] = " "
                            board[num[0] + 1][num[1]] = "tp"
                        else:
                            if board[num[0]][num[1]] == "p":
                                board[num[0]][num[1]] = " "
                            else:
                                board[num[0]][num[1]] = "t"
                            if board[num[0] + 1][num[1]] == "t":
                                board[num[0] + 1][num[1]] = "tp"
                            else:
                                board[num[0] + 1][num[1]] = "p"
                    except IndexError:
                        await ctx.send("Cant do that", delete_after=5)
                        continue
                elif inp == "left":
                    try:
                        num = self.get_player(board)
                        if (num[1] - 1) < 0:
                            await ctx.send("Cant go left any further", delete_after=5)
                            continue
                        elif board[num[0]][num[1] - 1] == "b":
                            if (num[1] - 2) < 0:
                                await ctx.send(
                                    "Cant push this box left any further",
                                    delete_after=5,
                                )
                                continue
                            if board[num[0]][num[1] - 2] == "b":
                                await ctx.send(
                                    "Can't push a 2 boxes at the same time",
                                    delete_after=5,
                                )
                                continue
                            if board[num[0]][num[1] - 2] == "t":
                                board[num[0]][num[1] - 2] = "tb"
                            else:
                                board[num[0]][num[1] - 2] = "b"
                            board[num[0]][num[1]] = " "
                            board[num[0]][num[1] - 1] = "p"
                        elif board[num[0]][num[1] - 1] == "tb":
                            if (num[1] - 2) < 0:
                                await ctx.send(
                                    "Cant push this box left any further",
                                    delete_after=5,
                                )
                                continue
                            if board[num[0]][num[1] - 2] == "b":
                                await ctx.send(
                                    "Can't push a 2 boxes at the same time",
                                    delete_after=5,
                                )
                                continue
                            if board[num[0]][num[1] - 2] == "t":
                                board[num[0]][num[1] - 2] = "tb"
                            else:
                                board[num[0]][num[1] - 2] = "b"
                            board[num[0]][num[1]] = " "
                            board[num[0]][num[1] - 1] = "tp"
                        else:
                            if board[num[0]][num[1]] == "p":
                                board[num[0]][num[1]] = " "
                            else:
                                board[num[0]][num[1]] = "t"
                            if board[num[0]][num[1] - 1] == "t":
                                board[num[0]][num[1] - 1] = "tp"
                            else:
                                board[num[0]][num[1] - 1] = "p"
                    except IndexError:
                        await ctx.send("Cant do that", delete_after=5)
                        continue
                elif inp == "right":
                    try:
                        num = self.get_player(board)
                        if (num[1] + 1) > len(board[0]) - 1:
                            await ctx.send("Cant go right any further", delete_after=5)
                            continue
                        elif board[num[0]][num[1] + 1] == "b":
                            if (num[1] + 2) < 0:
                                await ctx.send(
                                    "Cant push this box right any further",
                                    delete_after=5,
                                )
                                continue
                            if board[num[0]][num[1] + 2] == "b":
                                await ctx.send(
                                    "Can't push a 2 boxes at the same time",
                                    delete_after=5,
                                )
                                continue
                            if board[num[0]][num[1] + 2] == "t":
                                board[num[0]][num[1] + 2] = "tb"
                            else:
                                board[num[0]][num[1] + 2] = "b"
                            board[num[0]][num[1]] = " "
                            board[num[0]][num[1] + 1] = "p"
                        elif board[num[0]][num[1] + 1] == "tb":
                            if (num[1] + 2) < 0:
                                await ctx.send(
                                    "Cant push this box right any further",
                                    delete_after=5,
                                )
                                continue
                            if board[num[0]][num[1] + 2] == "b":
                                await ctx.send(
                                    "Can't push a 2 boxes at the same time",
                                    delete_after=5,
                                )
                                continue
                            if board[num[0]][num[1] + 2] == "t":
                                board[num[0]][num[1] + 2] = "tb"
                            else:
                                board[num[0]][num[1] + 2] = "b"
                            board[num[0]][num[1]] = " "
                            board[num[0]][num[1] + 1] = "tp"
                        else:
                            if board[num[0]][num[1]] == "p":
                                board[num[0]][num[1]] = " "
                            else:
                                board[num[0]][num[1]] = "t"
                            if board[num[0]][num[1] + 1] == "t":
                                board[num[0]][num[1] + 1] = "tp"
                            else:
                                board[num[0]][num[1] + 1] = "p"
                    except IndexError:
                        await ctx.send("Cant do that")
                        continue
                elif inp == "reset":
                    board = origin_board
                    origin_board = copy.deepcopy(board)
                em = discord.Embed(
                    title="Sokoban",
                    description=self.format_soko_board(board),
                    color=discord.Color.blurple(),
                )
                em.add_field(
                    name="Play",
                    value=f"Score: {diff_level}\nReact with a direction (up :arrow_up:, down :arrow_down:, right :arrow_right:, left :arrow_left:)",
                )
                await msg.edit(embed=em)
                if self.has_won_soko(board):
                    await ctx.send("Congrats, you won!", delete_after=10)
                    diff_level += 1
                    break
