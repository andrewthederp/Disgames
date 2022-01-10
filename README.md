<p align="center">
 <img src="./docs/src/disgames.png" height="125px" width="125px" />
</p>

<h1 align="center">Disgames</h1>
A python module made to make creating games easier and adds a bunch of game commands to your discord python bot

---
Note: The logo has been designed by using resources from [flaticon.com](https://www.flaticon.com/)


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

More examples on customizing the commands added to your bot can be seen in [`examples/`](./examples/)

And thats it! now your bot has the games implemented in [`disgames/mixins/`](./disgames/mixins/)

## Extra

Note that this works with the now discontinued module [discord.py](https://pypi.org/project/discord.py) and we
will make it compatible with other modules as soon as possible
