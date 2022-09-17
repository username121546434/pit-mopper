# Pit Mopper

Pit Mopper is a game based on "Minesweeper" that was built in python.

## Project Structure

### Folders

| Path To Folder | Purpose                                         |
| -------------- | ----------------------------------------------- |
| ./Scripts      | Python modules                                  |
| ./data         | Data files for Pit Mopper(ie: Images and Fonts) |

### Files

#### Root Directory

| Path To File       | Purpose                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------ |
| ./Pit Mopper.py    | Main Python file, run it to play the game                                                  |
| ./setup.py         | Python Script which compiles program to an EXE                                             |
| ./server.py        | Going to be the server for online multiplayer games                                        |
| ./requirements.txt | List of modules required. Simply use `pip install -r requirements.txt` to install them all |
| ./LICENSE.txt      | The License for Pit Mopper                                                                 |

#### Scripts Directory

| Path To File                | Purpose                                                                                                                             |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| ./Scripts/app.py            | Defines the `App` class                                                                                                             |
| ./Scripts/base_logger.py    | Defines the `init_logger` function which initializes the `logging` module                                                           |
| ./Scripts/console_window.py | Defines `get_console`, `show_console`, and `hide_console` functions, credits to [SO](https://stackoverflow.com/a/43314117)          |
| ./Scripts/constants.py      | Defines lots of constants and variables used by almost all of the files                                                             |
| ./Scripts/custom_menubar.py | Has the `CustomMenuBar` class which was taken and edited from [SO](https://stackoverflow.com/a/63208829)                            |
| ./Scripts/functions.py      | Defines many functions used by most files                                                                                           |
| ./Scripts/game.py           | Has a variety of game classes which are all dataclasses meaning they are used to store data                                         |
| ./Scripts/grid.py           | Defines the `ButtonGrid` and `PickleButtonGrid` classes which create a grid of `Squares`, used by some files                        |
| ./Scripts/load_font.py      | Has the `load_font` function for using fonts, only used by `squares.py`, also taken from [SO](https://stackoverflow.com/a/30631309) |
| ./Scripts/multiplayer.py    | A script that runs Pit Mopper in multiplayer mode                                                                                   |
| ./Scripts/network.py        | Has `Network` class which acts as a websocket connection to the server, also has `check_internet` function                          |
| ./Scripts/single_player.py  | A script that runs Pit Mopper in single player mode                                                                                 |
| ./Scripts/squares.py        | Defines the `Square` class which represents a single square on the grid of buttons                                                  |
| ./Scripts/updater.py        | Defines `check_for_updates` function which, well checks for updates and installs them                                               |

#### Other Files

| Path To File                           | Purpose                                                                               |
| -------------------------------------- | ------------------------------------------------------------------------------------- |
| ./data/fonts/DSEG7ClassicMini-Bold.ttf | A font used by the `Square` class. [DSEG Font](https://www.keshikan.net/fonts-e.html) |
| ./data/images/windows_icon.ico         | The logo for Pit Mopper on Windows                                                    |
| ./data/images/linux_icon.xbm           | The logo for Pit Mopper on Linux                                                      |

## Latest Features in v1.4.0

1. Added debug logging to help fight bugs
2. Added a console window
3. You can now delete data that it stores
