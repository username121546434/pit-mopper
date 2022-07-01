from cx_Freeze import setup, Executable

base = None    

executables = [Executable("./code/main.py", base='Win32GUI', icon='./code/data/images/logo.ico')]

packages = [
    "functools",
    'pickle',
    'tkinter',
    'os',
    'sys',
    'windows_tools.installed_software',
    'importlib',
    'importlib.util'
]
include_files = [
    './code/data'
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
    version = "1.1.0",
    description = '',
    executables = executables
)