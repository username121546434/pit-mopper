from functools import wraps
import threading
from typing import Callable


def thread(name: str | None = None, daemon: bool = False):
    """Simple decorator which puts the function wrapped in a new thread when called

    Args:
        name (str | None, optional): The name of the thread object. Defaults to None.
        daemon (bool, optional): Whether the thread is a daemon. Defaults to False.
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kw):
            t = threading.Thread(target=func, args=args, kwargs=kw, name=name, daemon=daemon)
            t.start()

        return wrapper
    
    return decorator
