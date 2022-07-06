from cx_Freeze import setup, Executable

base = None    

executables = [Executable(
    "./minesweeper-python/code/main.py",
    base='Win32GUI',
    icon='./minesweeper-python/code/data/images/logo.ico',
    copyright='GNU GPL v3, see LICENSE.txt for more info'
)]

packages = [
    "functools",
    'pickle',
    'tkinter',
    'os',
    'sys',
    'windows_tools.installed_software',
    'datetime',
    'ctypes',
    'grid',
    'updater',
    'squares',
    'load_font'
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
