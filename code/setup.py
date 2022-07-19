from cx_Freeze import setup, Executable

base = None    

executables = [Executable(
    "./pit-mopper/code/pit-mopper.py",
    base='Win32GUI',
    icon='./pit-mopper/code/data/images/logo.ico',
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
    './pit-mopper/code/data'
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
    version = "1.2.0",
    description = '',
    executables = executables
) 
