__all__ = [
    "logger",
    "rel_path",
    "stat_file",
    "Controller",
    "Export",
    "StateInteraction",
    "FileInteraction",
    "ColorInteraction",
    "IterationInteraction",
    "PositioningInteraction",
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
__author__ = "Dashstrom"

from .controller import Controller

from .view import (
    Export,
    StateInteraction,
    FileInteraction,
    ColorInteraction,
    IterationInteraction,
    PositioningInteraction,
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

from .util import logger, stat_file, rel_path
