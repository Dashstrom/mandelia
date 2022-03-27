import os
import sys

from datetime import datetime
from functools import wraps
from typing import Union

import tkinter as tk


def rel_path(relative_path: str) -> str:
    """Get path as relative path, pyinstaller compatible."""
    if hasattr(sys, '_MEIPASS'):
        dir_path = os.path.join(getattr(sys, "_MEIPASS"), "mandelia")
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


def sizeof_fmt(path: str) -> str:
    """Show information on a path."""
    size = float(os.path.getsize(path))
    for unit in ["", "k", "M", "G", "T", "P", "E", "Z"]:
        if abs(size) < 1000.0:
            return f"{size:3.1f}{unit}o"
        size /= 1000.0
    return f"{size:.1f}Yo"


def stat_file(path: str) -> str:
    """Show information on a path."""
    return f"Chemin : \"{path}\"\nTaille : {sizeof_fmt(path)}"


def set_icon(self: Union[tk.Toplevel, tk.Misc]) -> bool:
    """Set icon on tk.Misc or tk.TopLevel?"""
    try:
        icon = tk.PhotoImage(file=rel_path("view/images/logo.png"))
        self.tk.call("wm", "iconphoto", self._w, icon)  # type: ignore
        return True
    except Exception as err:
        print(err)
        return False
