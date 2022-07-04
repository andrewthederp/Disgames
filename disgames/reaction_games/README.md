## Reaction games documentation!
---
# Akinator
The Akinator class takes 1 arg and 3 kwargs
- Args
	- ctx (The command's context)
- Kwargs
	- child_mode (If set to `True` then the bot will only ask sfw questions, otherwise it will ask nsfw questions. `True` by default)
	- language (Decides what language the bot will be asking the questions in. `"en"` by default)
	- controls (Decides what reaction will do what. `{'1️⃣':'0', '2️⃣':'1', '3️⃣':'2', '4️⃣':'3', '5️⃣':'4', '🏳':'end', '⬅':'back'}` by default)

The start function of the Akinator class takes 0 args and 1 kwarg
- Kwarg
	- remove_reaction (If set to `True` then the bot remove the reaction provided by the user if possible. `False` by default)

# Connect4
The Connect4 class takes 1 arg and 4 kwargs
- Args
	- ctx (The command's context)
- Kwargs
	- red (The red player)
	- blue (The blue player)
	- format_dict (This dict will be used to format the board the player sees by replacing the key with the value. `{"r": "🔴","b": "🔵"," ": "⬛","R": "♦️","B": "🔷"}` by default)
	- controls (Decides what reaction will do what. `{'1️⃣':0,'2️⃣':1,'3️⃣':2,'4️⃣':3,'5️⃣':4,'6️⃣':5,'7️⃣':6,"🏳":'stop'}` by default)

The start function of the Connect4 class takes 0 args and 1 kwarg
- Kwarg
	- remove_reaction (If set to `True` then the bot remove the reaction provided by the user if possible. `False` by default)

# Snake
The Snake class takes 1 arg and 3 kwargs
- Args
	- ctx (The command's context)
- Kwargs
	- format_dict (This dict will be used to format the board the player sees by replacing the key with the value. `{'a':'🍎', 'h':'😳', 'b':'🟡', ' ':'⬛'}` by default)
	- board_size (The size of the snake board. `10` by default)
	- controls (Decides what reaction will do what. `{'⬆':UP:=(-1, 0), '⬇':DOWN:=(1, 0), '⬅':LEFT:=(0, -1), '➡':RIGHT:=(0, 1), '🏳️':'stop'}` by default)

The start function of the Snake class takes 0 args and 1 kwarg
- Kwarg
	- remove_reaction (If set to `True` then the bot remove the reaction provided by the user if possible. `False` by default)

# Soko
The Soko class takes 1 arg and 3 kwargs
- Args
	- ctx (The command's context)
- Kwargs
	- play_forever (A bool which determines if a new board should be created if the user wins. `False` by default)
	- format_dict (This dict will be used to format the board the player sees by replacing the key with the value. `{'p':'😳','tp':'😳','t':'❎','b':'🟫','bt':'✅',' ':'⬛','w':'⬜'}` by default)
	- board (If provided, it will attempt to create a game board out of the nested list which should look something like `[['w','w','w','w','w'],['w','p','b','t','w'],['w','w','w','w','w']]`. `None` by default, Note: You're responsible for making sure that the board is playable/winable (p > 0, t <= b))

The start function of the Soko class takes 0 args and 1 kwarg
- Kwarg
	- remove_reaction (If set to `True` then the bot remove the reaction provided by the user if possible. `False` by default)


# TicTacToe
The TicTacToe class takes 1 arg and 4 kwargs
- Args
	- ctx (The command's context)
- kwargs
	- x (The person playing as x)
	- o (The person playing as o)
	- format_dict (This dict will be used to format the board the player sees by replacing the key with the value. `{' ':'⬛','x':'❌','o':'⭕'}` by default)
	- controls (Decides what reaction will do what. `{'↖':(0,0), '⬆':(0,1), '↗':(0,2), '⬅':(1,0), '⏺':(1,1), '➡':(1,2), '↙':(2,0), '⬇':(2,1), '↘':(2,2), '🏳':'stop'}` by default)

The start function of the TicTacToe class takes 0 args and 1 kwarg
- Kwarg
	- remove_reaction (If set to `True` then the bot remove the reaction provided by the user if possible. `False` by default)
