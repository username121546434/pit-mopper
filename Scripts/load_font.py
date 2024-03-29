"""Taken from https://stackoverflow.com/a/30631309 and edited slightly"""
import os
from tkinter import font as tkfont

if os.name == 'nt':
    from ctypes import windll, byref, create_unicode_buffer, create_string_buffer
    FR_PRIVATE = 0x10
    FR_NOT_ENUM = 0x20


def load_font(fontpath, private=True, enumerable=False):
    '''
    Makes fonts located in file `fontpath` available to the font system.

    `private`     if True, other processes cannot see this font, and this 
                  font will be unloaded when the process dies
    `enumerable`  if True, this font will appear when enumerating fonts

    See https://msdn.microsoft.com/en-us/library/dd183327(VS.85).aspx

    '''
    if os.name != 'nt': # If not on windows, just use Comic Sans
        return 'Comic Sans'
    # This function was taken from
    # https://github.com/ifwe/digsby/blob/f5fe00244744aa131e07f09348d10563f3d8fa99/digsby/src/gui/native/win/winfonts.py#L15
    # This function is written for Python 2.x. For 3.x, you
    # have to convert the isinstance checks to bytes and str
    before = tkfont.families()
    if isinstance(fontpath, bytes):
        pathbuf = create_string_buffer(fontpath)
        AddFontResourceEx = windll.gdi32.AddFontResourceExA
    elif isinstance(fontpath, str):
        pathbuf = create_unicode_buffer(fontpath)
        AddFontResourceEx = windll.gdi32.AddFontResourceExW
    else:
        raise TypeError('fontpath must be of type str or unicode')

    flags = (FR_PRIVATE if private else 0) | (
        FR_NOT_ENUM if not enumerable else 0)
    numFontsAdded = AddFontResourceEx(byref(pathbuf), flags, 0)

    return [name for name in tkfont.families() if name not in before], bool(numFontsAdded)
