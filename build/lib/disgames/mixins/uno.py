import discord
from discord.ext import commands
import random

colors = ['red','yellow','blue','green','']
numbers = ['draw2','reverse','skip','wild','draw4'] + [str(i) for i in range(1,10)] # Names could be deceiving

class Card:
    def __init__(self, color, number):
        if number in ['wild','draw4']:
            self.color = ''
        else:
            self.color = color
        self.col = color
        self.number = number
        self.name = self.color+number
        self.type = 'normal' if number.isdecimal() else number

class Player:
    def __init__(self):
        self.cards = []
        for _ in range(5):
            self.cards.append(Card(random.choice(colors), random.choice(numbers)))
        self.inv = [card.name for card in self.cards]
        self.play = True

class Uno(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def convert_to_card(self, string):
        try:
            if int(string[-1]) in range(1, 10) and string[:-1] in colors:
                return Card(string[:-1], string[-1])
            else:
                raise ValueError
        except ValueError:
            for special in ['draw2', 'reverse', 'skip','wild','draw4']:
                if string.endswith(special) and string[:-len(special)] in colors:
                    return Card(string[:-len(special)], special)

    def cycle_uno_turns(self, lst):
        lst.append(lst[0])
        lst.pop(0)
        return lst, lst[0]

    def has_won_uno(self, player):
        return not len(player.cards)

    @commands.command()
    async def uno(self, ctx, players:commands.Greedy[discord.Member]):
        for player in players:
            if player.bot or player == ctx.author or not isinstance(player, discord.Member) or player in players:
                players.remove(player)
        if len(players) > 4:
            return await ctx.send("A maximum of 5 people that can play at the same time")
        elif len(players) <= 0:
            return await ctx.send("You need people to play with")
        decks = {}
        players.insert(0, ctx.author)
        turn = players[0]
        for player in players:
            decks[player] = Player()
        top_card = Card(random.choice(colors), random.choice(numbers))
        while top_card.number in ['draw2','reverse','skip','wild','draw4']:
            top_card = Card(random.choice(colors), random.choice(numbers))
        send = True
        while True:
            if len(players) <= 1:
                return await ctx.send("Gave over!")
            for player in players:
                if self.has_won_uno(decks[player]):
                    for player in players:
                        await player.send(f"{player.display_name} won uno!")
                    await ctx.send(f"{player.mention} won uno!")
                    players.remove(player)
            if not decks[turn].play:
                for player in players:
                    await player.send(f"{turn.display_name}'s turn has been skipped")
                decks[turn].play = True
                players, turn = self.cycle_uno_turns(players)
                continue
            if send:
                embed = discord.Embed(title=f'{turn.display_name} Inventory', description='\n'.join(decks[turn].inv), color=discord.Color.blurple())
                for player in players:
                    try:
                        await player.send(f'turn: {turn.display_name}\nThe top card is '+top_card.name, embed=embed if player == turn else None)
                    except discord.Forbidden:
                        return await ctx.send(f"I was unable to dm {player.mention}")
                send = False
            inp = await self.bot.wait_for('message', check = lambda m: m.author in players and not m.guild)
            if inp.content.lower() in ['inv','cards','deck']:
                embed = discord.Embed(title=f'{inp.author.display_name} Inventory', description='\n'.join(decks[inp.author].inv), color=discord.Color.blurple())
                await inp.author.send(embed=embed)
                continue
            elif inp.content.lower() in ['end','cancel','stop']:
                players.remove(inp.author)
                for player in players:
                    await player.send(f"{inp.author.display_name} leaves the game")
                continue
            else:
                if inp.author != turn:
                    continue
                if inp.content.lower() == 'draw':
                    card_drew = Card(random.choice(colors), random.choice(numbers))
                    await inp.author.send(f"You drew a {card_drew.name}")
                    decks[turn].inv.append(card_drew.name)
                    decks[turn].cards.append(card_drew)
                elif inp.content.lower() not in decks[turn].inv:
                    continue
                else:
                    card = self.convert_to_card(inp.content.lower())
                    if not card:
                        await inp.author.send("That's an invalid card name")
                        continue
                    if card.type == 'normal':
                        if card.color == top_card.color or card.number == top_card.number:
                            top_card = card
                            send = True
                            for thing in decks[turn].cards:
                                if thing.name == card.name:
                                    decks[turn].inv.remove(thing.name)
                                    decks[turn].cards.remove(thing)
                                    break
                            for player in players:
                                await player.send(f"{turn.display_name} played a {card.name}")
                            players, turn = self.cycle_uno_turns(players)
                        else:
                            await inp.author.send("That card cannot be played")
                    elif card.type == 'draw2':
                        if card.color == top_card.color or card.number == top_card.number:
                            top_card = card
                            send = True
                            next_turn = players[1]
                            for _ in range(2):
                                card_drew = Card(random.choice(colors), random.choice(numbers))
                                decks[next_turn].inv.append(card_drew.name)
                                decks[next_turn].cards.append(card_drew)
                                await next_turn.send(f'You drew a {card_drew.name}')
                            decks[next_turn].play = False
                            for thing in decks[turn].cards:
                                if thing.name == card.name:
                                    decks[turn].inv.remove(thing.name)
                                    decks[turn].cards.remove(thing)
                                    break
                            for player in players:
                                await player.send(f"{turn.display_name} played a {card.name}")
                            players, turn = self.cycle_uno_turns(players)
                        else:
                            await inp.author.send("That card cannot be played")
                    elif card.type == 'reverse':
                        if card.color == top_card.color or card.number == top_card.number:
                            top_card = card
                            send = True
                            for thing in decks[turn].cards:
                                if thing.name == card.name:
                                    decks[turn].inv.remove(thing.name)
                                    decks[turn].cards.remove(thing)
                                    break
                            turn = players[-1]
                            players = players[::-1]
                            for player in players:
                                await player.send(f'{inp.author.display_name} has reversed the play order')
                        else:
                            await inp.author.send("That card cannot be played")
                    elif card.type == 'skip':
                        if card.color == top_card.color or card.number == top_card.number:
                            top_card = card
                            send = True
                            next_turn = players[1]
                            decks[next_turn].play = False
                            for thing in decks[turn].cards:
                                if thing.name == card.name:
                                    decks[turn].inv.remove(thing.name)
                                    decks[turn].cards.remove(thing)
                                    break
                            for player in players:
                                await player.send(f"{turn.display_name} played a {card.name}")
                            players, turn = self.cycle_uno_turns(players)
                        else:
                            await inp.author.send("That card cannot be played")
                    elif card.type == 'wild':
                        await inp.author.send("Send the color to change to")
                        inp = await self.bot.wait_for('message', check=lambda m: m.author == inp.author and m.guild is None)
                        while inp.content.lower() not in colors:
                            await inp.author.send("Invalid, send the color to change to")
                            inp = await self.bot.wait_for('message', check=lambda m: m.author == inp.author and m.guild is None)
                        top_card = Card(inp.content, '')
                        send = True
                        for thing in decks[turn].cards:
                            if thing.name == card.name:
                                decks[turn].inv.remove(thing.name)
                                decks[turn].cards.remove(thing)
                                break
                        for player in players:
                            await player.send(f"{turn.display_name} played a {card.name}")
                        players, turn = self.cycle_uno_turns(players)
                    elif card.type == 'draw4':
                        await inp.author.send("Send the color to change to")
                        inp = await self.bot.wait_for('message', check=lambda m: m.author == inp.author and m.guild is None)
                        while inp.content not in colors:
                            await inp.author.send("Invalid, send the color to change to")
                            inp = await self.bot.wait_for('message', check=lambda m: m.author == inp.author and m.guild is None)
                        top_card = Card(inp.content, '')
                        send = True
                        next_turn = players[1]
                        for _ in range(4):
                            card_drew = Card(random.choice(colors), random.choice(numbers))
                            decks[next_turn].inv.append(card_drew.name)
                            decks[next_turn].cards.append(card_drew)
                            await next_turn.send(f'You drew a {card_drew.name}')
                        decks[next_turn].play = False
                        for thing in decks[turn].cards:
                            if thing.name == card.name:
                                decks[turn].inv.remove(thing.name)
                                decks[turn].cards.remove(thing)
                                break
                        for player in players:
                            await player.send(f"{turn.display_name} played a {card.name}")
                        players, turn = self.cycle_uno_turns(players)