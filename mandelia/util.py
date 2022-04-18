"""All utilities functions."""
import os
import sys

from datetime import datetime
from functools import wraps
from typing import Callable, TypeVar, Union, Optional
import tkinter as tk

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec


T = TypeVar('T')
P = ParamSpec('P')


def rel_path(relative_path: str) -> str:
    """Get path as relative path, pyinstaller compatible."""
    meipass: Optional[str] = getattr(sys, "_MEIPASS", None)
    frozen: bool = getattr(sys, 'frozen', False)
    if meipass is not None:
        dir_path = os.path.join(meipass, "mandelia")
    elif frozen:
        dir_path = os.path.dirname(sys.executable)
    else:
        dir_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir_path, relative_path)


def logger(function: Callable[P, T]) -> Callable[P, T]:
    """Log function by displaying arguments."""
    @wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        name = function.__qualname__
        str_args = ", ".join(repr(arg) for arg in args)  # type: ignore
        str_kwargs = ",".join("{}={!r}".format(k, arg)  # type: ignore
                              for k, arg in kwargs.items())  # type: ignore
        str_params = ",".join(part for part in (str_args, str_kwargs) if part)
        print("[{}] {}({})".format(datetime.now(), name, str_params))
        return function(*args, **kwargs)
    return wrapper


def sizeof_fmt(path: str) -> str:
    """Show information on a path."""
    size = float(os.path.getsize(path))
    for unit in ["", "k", "M", "G", "T", "P", "E", "Z"]:
        if abs(size) < 1000.0:
            return "{:3.1f}{}o".format(size, unit)
        size /= 1000.0
    return "{:.1f}Yo".format(size)


def stat_file(path: str) -> str:
    """Show information on a path."""
    return "Chemin : {}\nTaille : {}".format(repr(path), sizeof_fmt(path))


def set_icon(root: Union[tk.Toplevel, tk.Misc]) -> bool:
    """Set icon on tk.Misc or tk.TopLevel?"""
    try:
        icon = tk.PhotoImage(file=rel_path("view/images/logo.png"))
        root.tk.call("wm", "iconphoto", root._w, icon)  # type: ignore
        return True
    except OSError as err:
        print(err, file=sys.stderr)
        return False
