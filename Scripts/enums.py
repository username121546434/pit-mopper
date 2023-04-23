import sys

if sys.version_info.minor <= 10:
    from enum import Enum
else:
    from enum import StrEnum as Enum


class KBDShortcuts(Enum):
    """Contains all of the keyboard shorcuts used by Pit Mopper"""
    toggle_theme       =   '<Control-d>'
    check_for_updates  =   '<Control-u>'
    version_info       =   '<Control-i>'
    toggle_chording    =   '<Control-a>'
    reset_connection   =   '<Control-r>'
    open_file          =   '<Control-o>'
    show_highscores    =   '<Control-h>'
    save_file          =   '<Control-s>'
    start_game         =   '<space>'
    quit_game          =   '<Alt-q>'
    quit_app           =   '<Alt-F4>'
    game_info          =   '<Alt-i>'
    fullscreen         =   '<F11>'
