__all__ = [
    "logger",
    "call",
    "stat_file",
    "Controller",
    "Export",
    "Action",
    "File",
    "Color",
    "Iteration",
    "Positioning",
    "View",
    "Labeled",
    "VariableContainer",
    "AdjustableInput",
    "ModuloColoration",
    "Fractale",
    "Julia",
    "Mandelbrot",
    "FractaleManager"
]

__version__ = "1.0.1"
__author__ = "***REMOVED*** ***REMOVED***"

from .controller import logger, call, stat_file, Controller


from .view import (
    Export,
    Action,
    File,
    Color,
    Iteration,
    Positioning,
    View,
    Labeled,
    VariableContainer,
    AdjustableInput
)

from .model import (
    ModuloColoration,
    Fractale,
    Julia,
    Mandelbrot,
    FractaleManager
)