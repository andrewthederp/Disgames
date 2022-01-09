# Battleship

!!! danger
    Battleship right now is broken and will be fixed soon.

### What is Battleship

Battleship (also known as Battleships or Sea Battle) is a strategy type guessing game for two players. It is played on ruled grids (paper or board) on which each player's fleet of ships (including battleships) are marked. The locations of the fleets are concealed from the other player. Players alternate turns calling "shots" at the other player's ships, and the objective of the game is to destroy the opposing player's fleet.

Source: [Wikipedia](https://en.wikipedia.org/wiki/Battleship_(game))

### How to play

!!! warning

    Replace {prefix} with the prefix of your bot.

`{prefix}battleship [@user]`

!!! info  inline end
    Member is required parameter.

| Name | Requested Type |
| :-- | :-- |
| **Member** | Member ([discord.Member](https://docs.pycord.dev/en/master/api.html?highlight=member#discord.Member) e.g @user) |

![Sample](../src/screenshots/battleship.png)

### Permissions

??? tdlr "Permissions Required"
    | Name | Description |
    | :-- | :-- |
    | **Manage messages** | Manage messages |
    | **Send messages** | Send messages |
    | **Embed links** | Sending embeds |
    | **Add reactions** | Add reactions for games |

### Errors

??? tdlr "Possible Errors"
    | Name | Reason |
    | :-- | :-- |
    | **Member is required** | You did not input a user (Mention the user) |
    | **MissingPermissions** ([discord.ext.commands.BotMissingPermissions](https://docs.pycord.dev/en/master/ext/commands/api.html?highlight=missing#discord.ext.commands.BotMissingPermissions)) | You did not give the bot permission for it to play the game |
    | **Message NotFound** ([discord.NotFound](https://docs.pycord.dev/en/master/api.html?highlight=notfound#discord.NotFound)) | The message was deleted |
    | **TimeoutError** ([asyncio.TimeoutError](https://docs.python.org/3/library/asyncio-exceptions.html?highlight=timeouterror#asyncio.TimeoutError)) | You did not answer/respond in time. |

!!! tip
    If the error you got is not documented. Feel free to contribute [here](https://github.com/andrewthederp/Disgames/docs/mixins/battleship.md)
