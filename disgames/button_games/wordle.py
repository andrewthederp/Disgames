import discord
import copy
import random
import io

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


class WordleModal(discord.ui.Modal, title='Wordle'):
    def __init__(self, button):
        super().__init__()
        self.button = button

    inp = discord.ui.TextInput(
        label='Guess',
        placeholder='Type your guess here...'
    )

    async def on_submit(self, interaction):
        inp = self.inp.value.lower()
        view = self.button.view
        if not (interaction.user == view.ctx.author and inp not in [guess['guess'] for guess in view.guesses] and inp.isalpha() and len(inp) == 5):
            return

        view.tries += 1
        filter_word = view.filter_(inp)
        view.guesses.append({'guess':inp, 'filter_word':filter_word})
        await view.send_embed(interaction, view.has_won(filter_word), view.tries==6)
        if view.has_won(filter_word):
            view.winner = True
            view.stop()
        elif view.tries == 6:
            view.winner = False
            view.stop()


class Wordle(discord.ui.View):
    def __init__(self, ctx, *, word=None, image=False):
        super().__init__()

        from .. import ongoing_game_color, lost_game_color, won_game_color
        global ongoing_game_color, lost_game_color, won_game_color

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
        self.winner = 0

    async def interaction_check(self, interaction):
        if interaction.user == self.ctx.author:
            return True
        await interaction.response.send_message(content="This is not your game", ephemeral=True)

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
            if letter in word_copy:
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

    async def send_embed(self, interaction, win, lost):
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
                for child in self.children:
                    child.disabled = True
                return await interaction.response.edit_message(content='You won!', embed=embed, attachments=[f], view=self)
            if lost:
                embed.color = lost_game_color
                embed.set_footer(text=f"The word was: {self.word}")
                embed.set_image(url="attachment://wordle.png")
                for child in self.children:
                    child.disabled = True
                return await interaction.response.edit_message(content='You lost!', embed=embed, attachments=[f], view=self)
            embed.set_image(url="attachment://wordle.png")
            await interaction.response.edit_message(embed=embed, attachments=[f], view=self)
        else:
            if win:
                embed.color = won_game_color
                for child in self.children:
                    child.disabled = True
                return await interaction.response.edit_message(content='You won!', embed=embed, view=self)
            if lost:
                embed.color = lost_game_color
                embed.set_footer(text=f"The word was: {self.word}")
                for child in self.children:
                    child.disabled = True
                return await interaction.response.edit_message(content='You lost!', embed=embed, view=self)
            embed = self.make_embed()
            await interaction.response.edit_message(embed=embed)


    async def end_game(self, interaction):
        self.winner = False
        self.stop()
        for child in self.children:
            child.disabled = True
        embed = self.make_embed()
        embed.color = lost_game_color
        embed.set_footer(text=f"The word was: {self.word}")
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
            embed.set_image(url="attachment://wordle.png")
            await interaction.response.edit_message(embed=embed, attachments=[f], view=self)
        else:
            await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label='Guess', style=discord.ButtonStyle.blurple)
    async def guess(self, interaction, button):
        await interaction.response.send_modal(WordleModal(button))

    async def start(self, *, end_game_option=False):
        embed = self.make_embed()
        if self.image:
            path = '/'.join(__file__.split('/')[:-2])
            f = discord.File(f'{path}/assets/wordle.png', filename='wordle.png')
            embed.set_image(url="attachment://wordle.png")

        if end_game_option:
            button = discord.ui.Button(emoji='⏹', style=discord.ButtonStyle.danger)
            button.callback = self.end_game
            self.add_item(button)

        self.msg = await self.ctx.send(embed=embed, file=None if not self.image else f, view=self)
        await self.wait()
        return self.winner

