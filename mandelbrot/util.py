import os
import sys

from math import log, floor
from datetime import datetime
from functools import wraps


def rel_path(relative_path: str) -> str:
    """Get path as relative path, pyinstaller compatible."""
    if hasattr(sys, '_MEIPASS'):
        dir_path = getattr(sys, "_MEIPASS")
    elif getattr(sys, 'frozen', False):
        dir_path = os.path.dirname(sys.executable)
    else:
        dir_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir_path, relative_path)


def logger(func):
    """Log function by displaying arguments."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        str_args = ", ".join(f"{arg!r}" for arg in args)
        str_kwargs = ",".join(f"{k}={arg!r}" for k, arg in kwargs.items())
        str_params = ",".join(part for part in (str_args, str_kwargs) if part)
        print(f"[{datetime.now()}] {func.__qualname__}({str_params})")
        return func(*args, **kwargs)
    return wrapper


def stat_file(path: str) -> str:
    """Show information on a path."""
    size = os.path.getsize(path)
    step = 1024 
    if size < step:
        c = "o"
        echelle = step
    elif size < size ** 2:
        c = "k"
        echelle = step ** 2
    else:
        c = "M"
        echelle = step ** 3
    print(f"{size}/{echelle}={size / echelle}")
    return f"Chemin : \"{path}\"\nTaille : {size / echelle:.2f}{c}o"


if os.name == "nt":
    LOGO_PATH = rel_path("view/images/logo.ico")
else:
    LOGO_PATH = "@" + rel_path("view/images/logo.xbm")
    
