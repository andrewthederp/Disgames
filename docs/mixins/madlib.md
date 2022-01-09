# Madlib

### What is Madlib

Madlib is an api library that will allow you to create a paragraph by passing in a list of words as inputed.

### How to play

!!! warning

    Replace {prefix} with the prefix of your bot.

`{prefix}madlib [min] [max]`

!!! info  inline end
    Min and Max are optional parameter.

    Default min is 5 and max is 5.

| Name | Requested Type |
| :-- | :-- |
| **min** | ([int](https://docs.python.org/3/library/functions.html?highlight=int#int))|
| **max** | ([int](https://docs.python.org/3/library/functions.html?highlight=int#int))|

![Sample](../src/screenshots/madlib.png)

### Permissions

??? tdlr "Permissions Required"
    | Name | Description |
    | :-- | :-- |
    | **Manage messages** | Manage messages |
    | **Send messages** | Send messages |
    | **Embed links** | Sending embeds |

### Errors

??? tdlr "Possible Errors"
    | Name | Reason |
    | :-- | :-- |
    | **MissingPermissions** ([discord.ext.commands.BotMissingPermissions](https://docs.pycord.dev/en/master/ext/commands/api.html?highlight=missing#discord.ext.commands.BotMissingPermissions)) | You did not give the bot permission for it to play the game |
    | **BadArgument** ([discord.ext.commands.BadArgument](https://docs.pycord.dev/en/master/ext/commands/api.html?highlight=badargument#discord.ext.commands.BadArgument)) | You did not input what the parameter wanted |

!!! tip
    If the error you got is not documented. Feel free to contribute [here](https://github.com/andrewthederp/Disgames/docs/mixins/madlib.md)
