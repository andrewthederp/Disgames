import random, discord
from discord.ext import commands


class Sudoko(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def format_sudoko_board(self, board):
        """Format the sudoko board"""
        lst = ["  123 456 789"]
        for num, i in enumerate(board):
            scn_lst = []
            if num % 3 == 0 and num != 0:
                scn_lst += ["\n"]
            scn_lst += [str(num + 1)]
            for n, thing in enumerate(i):
                if n % 3 == 0:
                    scn_lst += [" "]
                scn_lst.append(thing)
            lst.append("".join(scn_lst))
        return "```\n" + "\n".join(lst) + "\n```"

    def create_sudoko_board(self, difficulty):
        """Creates the sudoko board and places x amount of numbers based on the difficulty"""
        board = [["0" for i in range(9)] for i in range(9)]
        if difficulty == 1:
            diff = random.randint(4, 6)
        elif difficulty == 2:
            diff = random.randint(9, 12)
        else:
            diff = random.randint(15, 19)
        for _ in range(diff):
            num = str(random.randint(1, 9))
            x = random.randint(0, 8)
            y = random.randint(0, 8)
            while num in board[x]:
                num = str(random.randint(1, 9))
            h = False
            for i in range(9):
                if num in board[i][y]:
                    h = True
                    break
            while h:
                num = str(random.randint(1, 9))
                h = False
                for i in range(9):
                    if num in board[i][y]:
                        break

            if x in range(3):
                x_ = 0
            elif x in range(3, 6):
                x_ = 3
            else:
                x_ = 6
            if y <= 3:
                y_ = 0
            elif y in range(3, 6):
                y_ = 3
            else:
                y_ = 6
            lst = [board[x_][y_]]
            lst += [
                board[x_ + 1][y_],
                board[x_ + 2][y_],
                board[x_][y_ + 1],
                board[x_][y_ + 2],
                board[x_ + 1][y_ + 1],
                board[x_ + 2][y_ + 2],
                board[x_ + 2][y_ + 1],
                board[x_ + 1][y_ + 2],
            ]
            while num in lst:
                num = str(random.randint(1, 9))
                if x in range(3):
                    x_ = 0
                elif x in range(3, 6):
                    x_ = 3
                else:
                    x_ = 6
                if y <= 3:
                    y_ = 0
                elif y in range(3, 6):
                    y_ = 3
                else:
                    y_ = 6
                lst = [board[x_][y_]]
                lst += [
                    board[x_ + 1][y_],
                    board[x_ + 2][y_],
                    board[x_][y_ + 1],
                    board[x_][y_ + 2],
                    board[x_ + 1][y_ + 1],
                    board[x_ + 2][y_ + 2],
                    board[x_ + 2][y_ + 1],
                    board[x_ + 1][y_ + 2],
                ]

            board[x][y] = num
        return board

    def has_won_sudoko(self, board):
        """Checks if game is over or not"""
        for x in board:
            for y in x:
                if y == "0":
                    return False
        return True

    @commands.command()
    async def sudoko(self, ctx):
        """puzzle in which players insert the numbers one to nine into a grid consisting of nine squares subdivided into a further nine smaller squares in such a way that every number appears once in each horizontal line, vertical line, and square."""
        m = await ctx.send("Enter a difficulty level: 1, 2, 3")
        difficulty = await self.bot.wait_for(
            "message",
            check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
        )
        await m.delete()
        try:
            difficulty = int(difficulty.content)
        except ValueError:
            return await ctx.send(
                "Invalid syntax: that's not a valid difficulty level", delete_after=5
            )
        if difficulty in range(1, 4):
            board = self.create_sudoko_board(difficulty)
        else:
            return await ctx.send(
                "Invalid syntax: that's not a valid difficulty level", delete_after=5
            )
        steps = []
        embed = discord.Embed(
            title="Sudoko",
            description=f"How to play: Insert the coordinates of where you want to play a number with the number after it, eg: `35 4`\n\n{self.format_sudoko_board(board)}",
            color=discord.Color.blurple(),
        ).set_footer(text='Send "end"/"stop"/"cancel" to stop the game')
        msg = await ctx.send(embed=embed)
        while True:
            embed = discord.Embed(
                title="Sudoko",
                description=f"How to play: Insert the coordinates of where you want to play a number with the number after it, eg: `35 4`\n\n{self.format_sudoko_board(board)}",
                color=discord.Color.blurple(),
            ).set_footer(text='Send "end"/"stop"/"cancel" to stop the game')
            await msg.edit(embed=embed)
            inp = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
            )
            if inp.content == "back":
                try:
                    board[steps[-1][0]][steps[-1][1]] = "0"
                    steps.pop(-1)
                    continue
                except IndexError:
                    await ctx.send(
                        "Invalid syntax: Cant go back any further", delete_after=5
                    )
                    continue
            elif inp.content.lower() in ["end", "stop", "cancel"]:
                await ctx.send("Ended the game", delete_after=5)
                return
            inp = inp.content.split(" ")
            try:
                x, y, num = int(inp[0][0]) - 1, int(inp[0][1]) - 1, int(inp[1])
            except (IndexError, ValueError):
                await ctx.send(
                    "You did not enter the coordinates correctly", delete_after=5
                )
                continue
            if x not in range(9) or y not in range(9):
                await ctx.send(
                    f"Invalid syntax: {x+1}{y+1} is not a valid place on the board",
                    delete_after=5,
                )
                continue
            steps.append((x, y))
            if int(board[x][y]) != 0:
                await ctx.send(
                    "Invalid syntax: Cant put a number there", delete_after=5
                )
                continue
            elif str(num) in board[x]:
                await ctx.send(
                    f"Invalid syntax: There is a another {str(num)} on the same row",
                    delete_after=5,
                )
                continue
            else:
                h = False
                for i in range(9):
                    if str(num) in board[i][y]:
                        h = True
                        break
                if h:
                    await ctx.send(
                        f"Invalid syntax: There is a another {str(num)} on the same column",
                        delete_after=5,
                    )
                    continue
                if x in range(3):
                    x_ = 0
                elif x in range(3, 6):
                    x_ = 3
                else:
                    x_ = 6
                if y in range(3):
                    y_ = 0
                elif y in range(3, 6):
                    y_ = 3
                else:
                    y_ = 6
                lst = [board[x_][y_]]
                lst += [
                    board[x_ + 1][y_],
                    board[x_ + 2][y_],
                    board[x_][y_ + 1],
                    board[x_][y_ + 2],
                    board[x_ + 1][y_ + 1],
                    board[x_ + 2][y_ + 2],
                    board[x_ + 2][y_ + 1],
                    board[x_ + 1][y_ + 2],
                ]
                if str(num) in lst:
                    await ctx.send(
                        f"Invalid syntax: There is a another {str(num)} on the same 3x3",
                        delete_after=5,
                    )
                    continue
                board[x][y] = str(num)
                if self.has_won_sudoko(board):
                    await ctx.send("You won sudoko!!!")
                    return
