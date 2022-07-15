from cx_Freeze import setup, Executable

base = None    

executables = [Executable(
    "./minesweeper-python/code/Minesweeper.py",
    base='Win32GUI',
    icon='./minesweeper-python/code/data/images/logo.ico',
    copyright='GNU GPL v3, see LICENSE.txt for more info'
)]

packages = [
    'grid',
    'updater',
    'squares',
    'load_font',
    'html.parser'
]
include_files = [
    './minesweeper-python/code/data'
]
options = {
    'build_exe': {    
        'packages':packages,
        'include_files':include_files
    },
}

setup(
    name = "Minesweeper",
    options = options,
    version = "1.2.0",
    description = '',
    executables = executables
) 
