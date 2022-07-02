import copy, discord
from discord.ext import commands


class Battleships(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.boards = {}

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, userr):
        """A way to switch between your board and your oponent's board"""
        if (
            userr.id in self.boards
            and not reaction.message.guild
            and reaction.message.author == self.bot.user
            and userr != self.bot.user
        ):
            try:
                if reaction.message.embeds[0].title == "Battleship":
                    if str(reaction) == "1️⃣":
                        embed = discord.Embed(
                            title="Battleship",
                            description=self.format_battleships_board(
                                self.boards[userr.id][0]
                            ),
                            color=discord.Color.blurple(),
                        )
                        await reaction.message.edit(embed=embed)
                    elif str(reaction) == "2️⃣":
                        embed = discord.Embed(
                            title="Battleship",
                            description=self.format_battleships_board(
                                self.boards[userr.id][1]
                            ),
                            color=discord.Color.red(),
                        )
                        await reaction.message.edit(embed=embed)
            except IndexError:
                pass

    def format_battleships_board(self, board):
        """Format the battleship board"""
        lst = ["⏹1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣"]
        dct = {}
        for i in range(1, 10):
            dct[i] = f"{i}\N{variation selector-16}\N{combining enclosing keycap}"
        for num, row in enumerate(board, start=1):
            scn_lst = [dct[num]]
            for column in row:
                scn_lst.append(column)
            lst.append("".join(scn_lst))
        return "\n".join(lst)

    def has_won_battleship(self, board):
        """Checks if either players died"""
        for x in board:
            for y in x:
                if y != "🌊" or y != "🔥":
                    return False
        return True

    @commands.command()
    async def battleship(self, ctx, member: discord.Member):
        if member.bot:
            return await ctx.send("Can't play with bots")
        elif member == ctx.author:
            return await ctx.send("Can't play with yourself")

        ships = [
            ["🚢", "🚢", "🚢", "🚢", "🚢"],
            ["🛥", "🛥", "🛥", "🛥"],
            ["⛵", "⛵", "⛵"],
            ["⛴", "⛴", "⛴"],
            ["🚤", "🚤"],
        ]

        dct = {"-": (0, 1), "|": (1, 0)}
        if ctx.author.id in self.boards:
            return await ctx.send("You are already in a game")
        elif member.id in self.boards:
            return await ctx.send(member.display_name + " is already in a game")
        self.boards[ctx.author.id] = [
            [["🌊" for _ in range(8)] for _ in range(8)],
            [["🌊" for _ in range(8)] for _ in range(8)],
        ]
        self.boards[member.id] = [
            [["🌊" for _ in range(8)] for _ in range(8)],
            [["🌊" for _ in range(8)] for _ in range(8)],
        ]
        embed = discord.Embed(
            title="Battleship",
            description=self.format_battleships_board(self.boards[ctx.author.id][0]),
            color=discord.Color.blurple(),
        )
        try:
            msg_1 = await ctx.author.send(embed=embed)
        except discord.Forbidden:
            del self.boards[ctx.author.id]
            del self.boards[member.id]
            return await ctx.send(f"I was unable to dm {ctx.author.display_name}")
        try:
            msg_2 = await member.send(f"Waiting for {ctx.author.display_name}")
        except discord.Forbidden:
            del self.boards[ctx.author.id]
            del self.boards[member.id]
            return await ctx.send(f"I was unable to dm {member.display_name}")
        turn = ctx.author
        other_turn = member
        ships_copy = copy.deepcopy(ships)
        for i, ship in enumerate(ships_copy):
            brd = copy.deepcopy(self.boards[ctx.author.id][0])
            await msg_1.edit(
                embed=discord.Embed(
                    title="Battleship",
                    description=self.format_battleships_board(
                        self.boards[ctx.author.id][0]
                    ),
                    color=discord.Color.blurple(),
                )
            )
            await ctx.author.send("Enter coordinates:")
            inp = await self.bot.wait_for(
                "message", check=lambda m: m.author in [ctx.author, member] and m.guild is None
            )
            if inp.content in ['end','stop','cancel']:
                await ctx.author.send(f"{inp.author.display_name} has ended the game")
                await member.send(f"{inp.author.display_name} has ended the game")
                del self.boards[ctx.author.id]
                del self.boards[member.id]
                return
            if inp.author != ctx.author:
                ships_copy.insert(i, ship)
                continue
            await ctx.author.send("up/down/left/right:")
            tru_dir = await self.bot.wait_for(
                "message", check=lambda m: m.author in [ctx.author, member] and m.guild is None
            )
            if tru_dir.content in ['end','stop','cancel']:
                await ctx.author.send(f"{tru_dir.author.display_name} has ended the game")
                await member.send(f"{tru_dir.author.display_name} has ended the game")
                del self.boards[ctx.author.id]
                del self.boards[member.id]
                return
            if tru_dir.author != ctx.author:
                ships_copy.insert(i, ship)
                continue
            if tru_dir.content.lower() not in ["up", "down", "left", "right"]:
                await ctx.author.send(
                    "Invalid syntax: Thats not a valid direction, try again",
                    delete_after=7.5,
                )
                ships_copy.insert(i, ship)
                self.boards[ctx.author.id][0] = brd
                continue
            direction = "|" if tru_dir.content.lower() in ["up", "down"] else "-"
            for num in range(len(ship)):
                try:
                    if tru_dir.content.lower() in ["down", "right"]:
                        x = (int(inp.content[0]) - 1) + dct[direction][0] * num
                        y = (int(inp.content[1]) - 1) + dct[direction][1] * num
                    else:
                        x = (int(inp.content[0]) - 1) - dct[direction][0] * num
                        y = (int(inp.content[1]) - 1) - dct[direction][1] * num
                    if x not in range(8) or y not in range(8):
                        await ctx.author.send(
                            "Invalid syntax: Cant add the ships there, try again!",
                            delete_after=7.5,
                        )
                        ships_copy.insert(i, ship)
                        self.boards[ctx.author.id][0] = brd
                        break
                    if self.boards[ctx.author.id][0][x][y] != "🌊":
                        await ctx.author.send(
                            "Invalid syntax: Cant have 2 ships overlap eachother, try again!",
                            delete_after=7.5,
                        )
                        ships_copy.insert(i, ship)
                        self.boards[ctx.author.id][0] = brd
                        break
                    self.boards[ctx.author.id][0][x][y] = ship[num]
                except IndexError:
                    await ctx.author.send(
                        "Invalid syntax: Cant add the ships there, try again!",
                        delete_after=7.5,
                    )
                    ships_copy.insert(i, ship)
                    self.boards[ctx.author.id][0] = brd
                    break
                except ValueError:
                    await ctx.author.send("Invalid syntax: invalid coordinates entered")
                    ships_copy.insert(i, ship)
                    self.boards[ctx.author.id][0] = brd
                    break

            await msg_1.edit(
                embed=discord.Embed(
                    title="Battleship",
                    description=self.format_battleships_board(
                        self.boards[ctx.author.id][0]
                    ),
                    color=discord.Color.blurple(),
                )
            )
        msg_1 = await ctx.author.send(
            embed=discord.Embed(
                title="Battleship",
                description=self.format_battleships_board(
                    self.boards[ctx.author.id][0]
                ),
                color=discord.Color.blurple(),
            )
        )
        await msg_1.add_reaction("1️⃣")
        await msg_1.add_reaction("2️⃣")
        await ctx.author.send(f"waiting for {member.display_name}")
        ship_copy = copy.deepcopy(self.boards[member.id][0])
        for i, ship in enumerate(ships_copy):
            brd = copy.deepcopy(self.boards[member.id][0])
            await member.send("Enter coordinates:")
            inp = await self.bot.wait_for(
                "message", check=lambda m: m.author in [ctx.author, member] and m.guild is None
            )
            if inp.content in ['end','stop','cancel']:
                await ctx.author.send(f"{inp.author.display_name} has ended the game")
                await member.send(f"{inp.author.display_name} has ended the game")
                del self.boards[ctx.author.id]
                del self.boards[member.id]
                return
            if inp.author != ctx.author:
                ships_copy.insert(i, ship)
                continue
            await ctx.author.send("up/down/left/right:")
            tru_dir = await self.bot.wait_for(
                "message", check=lambda m: m.author in [ctx.author, member] and m.guild is None
            )
            if tru_dir.content in ['end','stop','cancel']:
                await ctx.author.send(f"{tru_dir.author.display_name} has ended the game")
                await member.send(f"{tru_dir.author.display_name} has ended the game")
                del self.boards[ctx.author.id]
                del self.boards[member.id]
                return
            if tru_dir.author != ctx.author:
                ships_copy.insert(i, ship)
                continue
            if tru_dir.content.lower() not in ["up", "down", "left", "right"]:
                await member.send(
                    "Invalid syntax: Thats not a valid direction, try again",
                    delete_after=7.5,
                )
                ships_copy.insert(i, ship)
                self.boards[member.id][0] = brd
                continue
            direction = "|" if tru_dir.content.lower() in ["up", "down"] else "-"
            for num in range(len(ship)):
                try:
                    if tru_dir.content.lower() in ["down", "right"]:
                        x = (int(inp.content[0]) - 1) + dct[direction][0] * num
                        y = (int(inp.content[1]) - 1) + dct[direction][1] * num
                    else:
                        x = (int(inp.content[0]) - 1) - dct[direction][0] * num
                        y = (int(inp.content[1]) - 1) - dct[direction][1] * num
                    if x < 0 or y < 0:
                        await member.send(
                            "Invalid syntax: Cant add the ships there, try again!",
                            delete_after=7.5,
                        )
                        ships_copy.insert(i, ship)
                        self.boards[member.id][0] = brd
                        break
                    if self.boards[member.id][0][x][y] != "🌊":
                        await member.send(
                            "Invalid syntax: Cant have 2 ships overlap eachother, try again!",
                            delete_after=7.5,
                        )
                        ships_copy.insert(i, ship)
                        self.boards[member.id][0] = brd
                        break
                    self.boards[member.id][0][x][y] = ship[num]
                except IndexError:
                    await member.send(
                        "Invalid syntax: Cant add the ships there, try again!",
                        delete_after=7.5,
                    )
                    ships_copy.insert(i, ship)
                    self.boards[member.id][0] = brd
                    break
                except ValueError:
                    await member.send("Invalid syntax: invalid coordinates entered")
                    ships_copy.insert(i, ship)
                    self.boards[member.id][0] = brd
                    break

            await msg_2.edit(
                embed=discord.Embed(
                    title="Battleship",
                    description=self.format_battleships_board(
                        self.boards[member.id][0]
                    ),
                    color=discord.Color.blurple(),
                )
            )
        msg_2 = await member.send(
            embed=discord.Embed(
                title="Battleship",
                description=self.format_battleships_board(self.boards[member.id][0]),
                color=discord.Color.blurple(),
            )
        )
        await msg_2.add_reaction("1️⃣")
        await msg_2.add_reaction("2️⃣")
        while True:
            m = await turn.send("Enter coordinates to attack:")
            try:
                inp = await self.bot.wait_for(
                    "message", check=lambda m: m.author in [member, ctx.author] and m.guild is None, timeout=15*60
                )
            except asyncio.TimeoutError:
                del self.boards[ctx.author.id]
                del self.boards[member.id]
            if inp.content.lower() in ["end", "stop", "cancel"]:
                await member.send(f"{inp.author.display_name} ended the game")
                await ctx.author.send(f"{inp.author.display_name} ended the game")
                return
            if inp.author != turn:
                continue
            await m.delete()
            try:
                x, y = int(inp.content[0]) - 1, int(inp.content[1]) - 1
            except (IndexError, ValueError):
                await turn.send("Invalid syntax: invalid coordinates entered")
                continue
            if x not in range(8) or y not in range(8):
                await turn.send(
                    f"Invalid Syntax: {x+1}{y+1} isn't a valid place on the board"
                )
                continue
            if self.boards[other_turn.id][0][x][y] not in ["🌊", "🔥"]:
                await turn.send(f"You fired at {x+1}{y+1} and it was a hit!")
                await other_turn.send(
                    f"{turn.display_name} fired at {x+1}{y+1} and it was a hit :pensive:"
                )
            else:
                await turn.send(f"You fired at {x+1}{y+1} and missed :pensive:")
                await other_turn.send(
                    f"{turn.display_name} fired at {x+1}{y+1} and missed!"
                )
            self.boards[other_turn.id][0][x][y] = "🔥"
            self.boards[turn.id][1][x][y] = "❌"
            if self.has_won_battleship(self.boards[other_turn.id][0]):
                await ctx.author.send(f"{turn.display_name} has won!!!")
                await member.send(f"{turn.display_name} has won!!!")
                del self.boards[ctx.author.id]
                del self.boards[member.id]
                return
            other_turn = turn
            turn = member if turn == ctx.author else ctx.author
            await msg_2.edit(
                embed=discord.Embed(
                    title="Battleship",
                    description=self.format_battleships_board(
                        self.boards[member.id][0]
                    ),
                    color=discord.Color.blurple(),
                )
            )
            await msg_1.edit(
                embed=discord.Embed(
                    title="Battleship",
                    description=self.format_battleships_board(
                        self.boards[ctx.author.id][0]
                    ),
                    color=discord.Color.blurple(),
                )
            )