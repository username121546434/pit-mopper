"""Python Script which compiles program to an EXE"""
from Scripts.constants import VERSION, LOGO
import os
from cx_Freeze import setup, Executable

base = 'Win32GUI' if os.name == 'nt' else None
icon = LOGO if os.name == 'nt' else LOGO[1:]

executables = [Executable(
    "./Pit Mopper.py",
    base=base,
    icon=icon,
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
    version = VERSION,
    description = '',
    executables = executables
) 
