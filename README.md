A python module made to make creating games easier and adds a bunch of game commands to your discord python bot

---
## Contents

- [Disgames](#disgames)
  - [Contents](#contents)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Configuration](#configuration)
  - [Winnings](#winnings)
  - [Example](#example)
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

- Import the class of the game you want from the controls type you want
  - E.g. `from disgames.button_games import Chess`
- Create an instance of the class while providing the necessary args/kwargs
  - E.g. `game = Chess(ctx, white=ctx.author, black=member)`
- Start the game by running the start function and providing the necessary args/kwargs
  - E.g. `game.start(end_game_option=True)`

More examples can be seen in [`examples/`](./examples/)

## Configuration
You can configure some variables that are used throughout the module
- `disgames.ongoing_game_color` The color of the embed while the game is still running
- `disgames.lost_game_color` The color of the embed when the player looses (only used in singleplayer games)
- `disgames.won_game_color` The color of the embed when the player wins
- `isgames.drawn_game_color` The color of the embed when the game draws
- `disgames.resend_embed_list` A list of strings, if the player sends a message which is in the list. The game embed will be re-sent (only used in message games)
- `disgames.end_game_list` A list of strings, if the player sends a message which is in the list. The game will end (only used in message games)

Example of changing a variable: `disgames.drawn_game_color = 0x000000`

## Winnings
The start function will return any of `discord.Member`/`True`/`False`/`None`/`list`
`True`/`False` will only be returned if the game is a single player game and it means the author has won/lost
`None` means the game has ended in a draw
`discord.Member` means that that person has won the game
`list` would be a list of bools, this is only returned by `Soko`. A `True` will be added into the list for every game the user wins. And the last item in the list will always be `False` if `play_forever` is set to `True`

## Examples
Coming soon!

## Extra
Note that this package only works with [discord.py](https://pypi.org/project/discord.py) and other modules that use the `discord` namespace