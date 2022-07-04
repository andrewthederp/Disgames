import discord
import copy
import random
import io

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

class Wordle:
    def __init__(self, ctx, *, word=None, image=False):

        from .. import end_game_list, ongoing_game_color, lost_game_color, won_game_color
        global end_game_list, ongoing_game_color, lost_game_color, won_game_color

        self.ctx = ctx
        path = '/'.join(__file__.split('/')[:-2])
        self.ctx = ctx
        self.words = []
        for word_ in open(f'{path}/assets/words.txt').readlines():
            word_ = word_.replace('\r','').strip()
            if len(word_) == 5 and word_.isalpha():
                self.words.append(word_)
        self.word = (word or random.choice(self.words)).lower()
        self.guesses = []
        self.tries = 0
        self.image = image


    def remove(self, wrd, letter):
        wrd = list(wrd)
        wrd[wrd.index(letter)] = " "
        return ''.join(wrd)

    def filter_(self, guess):
        arr = ['','','','','']
        word_copy = copy.deepcopy(self.word)

        for i, letter in enumerate(guess):
            if letter == word_copy[i]:
                word_copy = self.remove(word_copy,letter)
                arr[i] = '🟩'

        for i, letter in enumerate(guess):
            if letter in word_copy and not arr[i]:
                word_copy = self.remove(word_copy,letter)
                arr[i] = '🟨'

        for num, i in enumerate(arr):
            if not i:
                arr[num] = '🟥'

        return ''.join(arr)

    def has_won(self, arr):
        return arr == '🟩🟩🟩🟩🟩'

    def make_embed(self):
        string = ''
        embed = discord.Embed(title='Wordle', description='', color=ongoing_game_color)
        if not self.image:
            for guess in self.guesses:
                embed.description += f"{''.join([f':regional_indicator_{i}:' for i in guess['guess']])}\n{guess['filter_word']}\n"
        return embed

    async def send_embed(self, win, lost):
        embed = self.make_embed()
        if self.image:
            sqr_wdth = 91
            sqr_hght = 91
            x_sep = 8
            y_sep = 11
            x_offset = 11
            y_offset = -6
            path = '/'.join(__file__.split('/')[:-2])

            img = Image.open(f'{path}/assets/wordle.png')
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(f"{path}/assets/arialbd.ttf", 80)

            for row, dct in enumerate(self.guesses):
                guess = dct['guess']
                filter_word = dct['filter_word']
                for col, letter in enumerate(guess):
                    cir = filter_word[col]
                    if cir == '🟩':
                        rgb = (46,204,113)
                    elif cir == '🟨':
                        rgb = (255,212,69)
                    else:
                        rgb = (231,76,60)
                    xy = col*sqr_hght, row*sqr_wdth
                    for x in range(xy[1], ((row*sqr_wdth)+sqr_wdth)-x_sep):
                        for y in range(xy[0], ((col*sqr_hght)+sqr_hght)-y_sep):
                            img.putpixel((y,x), rgb)
                    draw.text((xy[0]+x_offset, xy[1]+y_offset), letter.upper(), (255,255,255), font=font)
            arr = io.BytesIO()
            img.save(arr, format='PNG')
            arr.seek(0)
            f = discord.File(arr, filename='wordle.png')

            if win:
                embed.color = won_game_color
                embed.set_image(url="attachment://wordle.png")
                return await self.msg.edit(content='You won!', embed=embed, attachments=[f])
            if lost:
                embed.color = lost_game_color
                embed.set_footer(text=f"The word was: {self.word}")
                embed.set_image(url="attachment://wordle.png")
                return await self.msg.edit(content='You lost!', embed=embed, attachments=[f])
            embed.set_image(url="attachment://wordle.png")
            await self.msg.edit(embed=embed, attachments=[f])
        else:
            if win:
                embed.color = won_game_color
                return await self.msg.edit(content='You won!', embed=embed)
            if lost:
                embed.color = lost_game_color
                embed.set_footer(text=f"The word was: {self.word}")
                return await self.msg.edit(content='You lost!', embed=embed)
            embed = self.make_embed()
            await self.msg.edit(embed=embed)



    async def start(self, *, delete_input=False, end_game_option=False):
        embed = self.make_embed()
        if self.image:
            path = '/'.join(__file__.split('/')[:-2])
            f = discord.File(f'{path}/assets/wordle.png', filename='wordle.png')
            embed.set_image(url="attachment://wordle.png")
        self.msg = await self.ctx.send(embed=embed, file=None if not self.image else f)
        while True:
            inp = await self.ctx.bot.wait_for('message', check=lambda m: m.author == self.ctx.author and m.channel == self.ctx.channel and m.content.lower() not in [guess['guess'] for guess in self.guesses])


            if end_game_option and inp.content.lower() in end_game_list:
                embed = self.make_embed()
                embed.color = lost_game_color
                await self.msg.edit(content='Game ended', embed=embed)
                return False

            if not (inp.content.isalpha() and len(inp.content) == 5):
                continue

            if delete_input:
                try:
                    await inp.delete()
                except discord.Forbidden:
                    pass

            self.tries += 1
            filter_word = self.filter_(inp.content.lower())
            self.guesses.append({'guess':inp.content.lower(), 'filter_word':filter_word})
            await self.send_embed(self.has_won(filter_word), self.tries==6)
            if self.has_won(filter_word) or self.tries == 6:
                break
        if self.has_won(filter_word):
            return True
        else:
            return False
