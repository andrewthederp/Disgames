# Changelog

The changelogs are on [github](https://github.com/andrewthederp/disgames/releases)

## [2.0.1](https://github.com/andrewthederp/Disgames/releases/tag/2.0.1) (2021-12-12)

Minor Bug fixes:

* Fixed bug in connect4 where it would say a tie even if the move was a win if it was the last move possible on the board
* Fixed bug in chess where the turn would change if the other person sends a message
* Fixed bug in hangman where it try to turn strings like `|` into an emoji by doing `:regional_indicator_|:`
* Fixed bug in RPS where it would consider the bot's reaction as input
* Changed in hangman if you send a word that isn't the same as the word they are supposed to guess it will count as an error

## [v2.0.0](https://github.com/andrewthederp/Disgames/releases/tag/2.0.0) (2021-12-10)

Fixed:

* Fixed AttributeError in `register_commands` and `Bot.load_extension`
* Fixed a bug in RPS which never seemed to exist
* Fixed bomb-to-numbers ratio in minesweeper

Added:

* You can now manually provide a path to the `stockfish_20011801_32bit.exe` through `disgames.reigster_commands`
* Cannot be provided while using Bot.load_extension
* When not provided, it would find the `stockfish_20011801_32bit.exe` file in `C:\Users\USER-NAME PC` and use that instead
* Raises disgames.errors.PathNotFound when no `stockfish_20011801_32bit.exe` was found
* If you don't already have it, you can install it here
* Added `errors.py`
* Added `PathNotFound` in `errors.py`

## [v1.4.0](https://github.com/andrewthederp/Disgames/releases/tag/1.4.0) (2021-11-17)

* Added `minesweeper`, `sokoban`, `RPS`
* Fix stockfish path bug

## [v1.3.1](https://github.com/andrewthederp/Disgames/releases/tag/1.3.1) (2021-11-8)

* Bug fixes
* Better way to send requests
* Add examples
* Removed support for `Bot.add_command` method

## [v1.1.0](https//github.com/andrewthederp/Disgames/releases/tag/1.1.0) (2021-10-30)

* Added Chess, Hangman, Madlib, Tictactoe
* Chess AI
* `register_commands` function
