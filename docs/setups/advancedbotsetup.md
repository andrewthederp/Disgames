# Advance Bot Setup

Your probably gonna need to add some disgames to your bot but the basic bot setup isn't how you set up your bot. You probadly gonna need some help here. Here how to do it.

You might set up your bot like this:

```python
from discord.ext import commands
import discord

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.all())
```

Well It's pretty simple to add disgames to your bot. Inside of __init__ function add this line of code to your bot:

```python
register_commands(self, ignore=[], stockfish_path=None)
```

So your bot `__init__` function would look like this:

!!! tip
    Stockfish path is optional. If you want to input it. Please choose stockfish as stockfish_20011801_32bit.exe. You can rename it to that

    Ignore only takes in a list of commands you want to ignore. E.g. ignore=[Chess] Where Chess is imported like
    
    `from disgames.mixins.chess import Chess`

```python
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.all())
        register_commands(self, ignore=[], stockfish_path=None)
```

!!! tip
    If this not how you settled up your bot. Feel free to contribute [here](https://github.com/andrewthederp/disgames)
