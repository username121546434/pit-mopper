# Pit Mopper

Pit Mopper is a game based on "Minesweeper" that was built in python.

## Project Structure

### Folders

| Path To Folder | Purpose                                         |
| -------------- | ----------------------------------------------- |
| ./Scripts      | Python modules                                  |
| ./Scripts/data | Data files for Pit Mopper(ie: Images and Fonts) |

### Files

#### Root Directory

| Path To File      | Purpose                                                                                   |
| ----------------- | ----------------------------------------------------------------------------------------- |
| ./Pit Mopper.py   | Main Python file, run it to play the game                                                 |
| ./setup.py        | Python Script which compiles program to an EXE                                            |
| ./server.py       | Going to be the server for online multiplayer games                                       |
| ./requirments.txt | List of modules required. Simply use `pip install -r requirments.txt` to install them all |
| ./LICENSE.txt     | The Liecense for Pit Mopper                                                               |

#### Scripts Directory

| Path To File                | Purpose                                                                                                                                  |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| ./Scripts/app.py            | Defines the `App` class                                                                                                                  |
| ./Scripts/base_logger.py    | Defines the `init_logger` function which initializes the `logging` module                                                                |
| ./Scripts/console_window.py | Defines `get_console`, `show_console`, and `hide_console` functions, credits to [SO](https://stackoverflow.com/a/43314117)               |
| ./Scripts/constants.py      | Defines lots of constants and variables used by almost all of the files                                                                  |
| ./Scripts/custom_menubar.py | Has the `CustomMenuBar` class which was taken and edited from [SO](https://stackoverflow.com/a/63208829)                                 |
| ./Scripts/functions.py      | Defines many functions used by most files                                                                                                |
| ./Scripts/game.py           | Has the `OnlineGame` class, only used by `server.py` and `multiplayer.py`                                                                |
| ./Scripts/grid.py           | Defines the `ButtonGrid` and `PickleButtonGrid` classes which create a grid of `Squares`, used by some files                             |
| ./Scripts/load_font.py      | Has the `load_font` function for installing fonts, only used by `squares.py`, also taken from [SO](https://stackoverflow.com/a/30631309) |
| ./Scripts/multiplayer.py    | A script that runs Pit Mopper in multiplayer mode                                                                                        |
| ./Scripts/network.py        | Has `Network` class which acts as a websocket connection to the server, also has `check_internet` function                               |
| ./Scripts/single_player.py  | A script that runs Pit Mopper in single player mode                                                                                      |
| ./Scripts/squares.py        | Defines the `Square` class which represents a single square on the grid of buttons                                                       |
| ./Scripts/updater.py        | Defines `check_for_updates` function which, well checks for updates and installs them                                                    |

#### Other Files

| Path To File                                   | Purpose                                                                               |
| ---------------------------------------------- | ------------------------------------------------------------------------------------- |
| ./Scripts/data/fonts/DSEG7ClassicMini-Bold.ttf | A font used by the `Square` class. [DSEG Font](https://www.keshikan.net/fonts-e.html) |
| ./Scripts/data/images/windows_icon.ico         | The logo for Pit Mopper on Windows                                                    |
| ./Scripts/data/images/linux_icon.xbm           | The logo for Pit Mopper on Linux                                                      |

## Keyboard Shortcuts

List of all keyboard shortcuts currently in game

### Global Keyboard Shorcuts

These Shortcuts can be used anywhere except sometimes in a game

| Shortcut | What it does                                                         |
| :------- | -------------------------------------------------------------------- |
| Ctrl + I | Shows the Version of Pit Mopper                                      |
| Ctrl + U | Checks for updates                                                   |
| Ctrl + Q | Quits Pit Mopper, same as just clicking the "X" button on the window |
| Ctrl + D | Enables/Disables Dark Mode                                           |
| Ctrl + X | Shows/Hides Console window                                           |

### Single Player Shortcuts

These shortcuts can only be used in single player
| Shortcut | What it does                                                                      |
| :------- | --------------------------------------------------------------------------------- |
| Ctrl + O | Loads a game from a Pit Mopper game file                                          |
| Ctrl + A | Enables/Disables Chording                                                         |
| Space    | Does the same thing that the "Play!" button in the single player game loader does |
| Ctrl + H | Shows your highscores                                                             |

### Multiplayer Shortcuts

These shortcuts are only available in multiplayer mode

| Shortcut | What it does                                                     |
| :------- | ---------------------------------------------------------------- |
| Ctrl + R | Disconnects and reconnects from the server, useful for debugging |

### In Game Shorcuts

These shortcuts are only available when a game has started

| Shortcut | What it does                                                               |
| :------- | -------------------------------------------------------------------------- |
| F11      | Toggles whether the game window is in fullscreen or not                    |
| Alt + Q  | Closes the current game being played                                       |
| Alt + I  | Gives extra information about the current game, only in single player mode |
| Ctrl + S | Saves the current game being played, only in single player mode            |

## Latest Features in v1.4.0

1. Added debug logging to help fight bugs
2. Added a console window
3. You can now delete data that it stores
