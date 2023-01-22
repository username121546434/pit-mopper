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
    'html.parser', # Required by the markdown library
    'tkinterweb'
]

include_files = [
    ('./data/fonts', 'data/fonts'),
]

if os.name == 'nt':
    include_files.append(('./data/images/windows_icon.ico', 'data/images/windows_icon.ico'))
    include_files.append(('./data/images/windows_icon_darkmode.ico', 'data/images/windows_icon_darkmode.ico'))
else:
    include_files.append(('./data/images/linux_icon.xbm', './data/images/linux_icon.xbm'))
    include_files.append(('./data/images/linux_icon_darkmode.xbm', './data/images/linux_icon_darkmode.xbm'))

options = {
    'build_exe': {
        'packages': packages,
        'include_files': include_files
    },
}

setup(
    name = "Pit Mopper",
    options = options,
    version = VERSION,
    description = '',
    executables = executables
)
