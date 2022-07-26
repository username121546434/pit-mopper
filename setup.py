from cx_Freeze import setup, Executable

base = None    

executables = [Executable(
    "./Pit Mopper.py",
    base='Win32GUI',
    icon='./Scripts/data/images/logo.ico',
    copyright='GNU GPL v3, see LICENSE.txt for more info'
)]

packages = [
    'html.parser'
]
include_files = [
    './Scripts/data'
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
