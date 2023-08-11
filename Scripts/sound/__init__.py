from os import name

if name == 'nt':
    from .windows import play
else:
    from .linux import play
