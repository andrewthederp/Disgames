# Disgames

A python module made to make creating games easier and adds a bunch of game commands to your discord python bot

## Contents

- [Disgames](#disgames)
  - [Contents](#contents)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Extra](#extra)

## Installation

To install it from [pypi](https://pypi.org/project/disgames), run

```sh
pip install disgames
```

To install the development version, you need [git](https://git-scm.com/downloads) installed. After installing it, run

```shell
pip install git+https://github.com/andrewthederp/Disgames
```

## Usage

You can either load it as an extension by doing

```py
from discord.ext import commands

bot = commands.Bot("YOUR_PREFIX_HERE")

bot.load_extension("disgames")
```

or call the `register_commands` function manually by doing

```py
from disgames import register_commands
from discord.ext import commands

bot = commands.Bot("YOUR_PREFIX_HERE")
register_commands(bot)
```

If you want more control over what commands are added to your bot, you can use the ignore kwarg

```py
from disgames import register_commands, Chess
from discord.ext import commands

bot = commands.Bot("YOUR_PREFIX_HERE")
register_commands(bot, ignore=[Chess])
```

If you instead want **only** one command, you can add the cog manually like this

```py
from disgames import Chess
from discord.ext import commands

bot = commands.Bot("YOUR_PREFIX_HERE")
bot.add_cog(Chess(bot))
```

And thats it! now your bot has the games implemented in [`disgames/mixins/`](./disgames/mixins/)

## Extra

Note that this works with the now discontinued module [discord.py](https://pypi.org/project/discord.py) and we
will make it compatible with other modules as soon as possible
