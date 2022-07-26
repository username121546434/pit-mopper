from cx_Freeze import setup, Executable

base = None    

executables = [Executable(
    "./pit-mopper/Pit Mopper.py",
    base='Win32GUI',
    icon='./pit-mopper/Scripts/data/images/logo.ico',
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
    './pit-mopper/Scripts/data'
]
options = {
    'build_exe': {    
        'packages':packages,
        'include_files':include_files
    },
}

setup(
    name = "Pit Mopper",
    options = options,
    version = "1.4.0",
    description = '',
    executables = executables
) 
