import os
import re
import subprocess
from typing import Literal
if os.name == 'nt':
    import winreg
from .constants import PROTOCOL, APP_EXE, HOME, LOGO


def _register_protocol_windows():
    """
    Registers `ptmpr://` as a url protocol on windows
    """
    if os.name != 'nt':
        return
    # define the registry key to be modified
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, f'Software\\Classes\\{PROTOCOL}')

    # set the default value of the key
    winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f"URL:{PROTOCOL} Protocol")
    winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")

    # create the DefaultIcon subkey
    icon_key = winreg.CreateKey(key, "DefaultIcon")
    winreg.SetValueEx(icon_key, "", 0, winreg.REG_SZ, f'"{APP_EXE}"')

    # create the shell subkey
    shell_key = winreg.CreateKey(key, "shell")
    open_key = winreg.CreateKey(shell_key, "open")
    command_key = winreg.CreateKey(open_key, "command")
    winreg.SetValueEx(command_key, "", 0, winreg.REG_SZ, f'"{APP_EXE}" "%1"')

    # close the registry keys
    winreg.CloseKey(command_key)
    winreg.CloseKey(open_key)
    winreg.CloseKey(shell_key)
    winreg.CloseKey(icon_key)
    winreg.CloseKey(key)


def _has_been_registered_windows():
    """
    Checks if `ptmpr://` has been registered as a url protocol in windows

    Returns: `True` or `False` if `ptmpr://` has been registered
    """
    if os.name != 'nt':
        return
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"{PROTOCOL}", 0, winreg.KEY_READ)
        winreg.CloseKey(key)
        icon_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"{PROTOCOL}\\DefaultIcon", 0, winreg.KEY_READ)
        winreg.CloseKey(icon_key)
        shell_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"{PROTOCOL}\\shell", 0, winreg.KEY_READ)
        winreg.CloseKey(shell_key)
        open_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"{PROTOCOL}\\shell\\open", 0, winreg.KEY_READ)
        winreg.CloseKey(open_key)
        command_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"{PROTOCOL}\\shell\\open\\command", 0, winreg.KEY_READ)
        winreg.CloseKey(command_key)
        return True
    except WindowsError:
        return False


def _register_protocol_ubuntu():
    """
    Registers `ptmpr://` as a url protocol on ubuntu
    """
    if os.name == 'nt':
        return
    with open(os.path.join(HOME, ".local/share/applications/ptmpr.desktop"), "w") as file:
        file.writelines('\n'.join((
            "[Desktop Entry]",
            "Type=Application",
            "Name=Pit Mopper",
            f'Icon={os.path.join(os.getcwd(), LOGO.strip("@"))}',
            r'Exec=ptmpr-open.sh %u',
            "StartupNotify=false",
            "MimeType=x-scheme-handler/ptmpr",
        )))
    
    # required because for some reason, xdg-open does not like spaces in filenames
    with open(os.path.join(HOME, '.local/bin/ptmpr-open.sh'), 'w') as f:
        f.write(f'"{APP_EXE}" $1')
    
    os.system('chmod +x .local/bin/ptmpr-open.sh')
    os.system('xdg-mime default ptmpr.desktop x-scheme-handler/ptmpr')
    

def _has_been_registered_ubuntu():
    """
    Checks if `ptmpr://` has been registered as a url protocol in ubuntu

    Returns: `True` or `False` if `ptmpr://` has been registered
    """
    if os.name == 'nt':
        return
    result = subprocess.run(['xdg-mime', 'query', 'default', 'x-scheme-handler/ptmpr'], stdout=subprocess.PIPE)
    if not result.stdout:
        return False
    
    return True


def has_been_registered():
    if os.name == 'nt':
        return _has_been_registered_windows()
    else:
        return _has_been_registered_ubuntu()


def register_protocol():
    if os.name == 'nt':
        return _register_protocol_windows()
    else:
        return _register_protocol_ubuntu()


def parse_url(s: str) -> tuple[Literal['m'], str | None, int | None, int | None] | tuple[Literal['s'], None, None, None] | None:
    pattern = re.compile(r'ptmpr://(?P<mode>s|m)/(?P<server>[^:]+)?:?(?P<port>\d+)?/?(?P<id>\d+)?$')
    match = pattern.search(s)
    if match:
        mode = match.group('mode')
        if mode == "m":
            server = match.group('server') if match.group('server') else None
            port = int(match.group('port')) if match.group('port') else None
            id = int(match.group('id')) if match.group('id') else None
            return (mode, server, port, id)
        elif mode == 's':
            return (mode, None, None, None)
    else:
        return None
