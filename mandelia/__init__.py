"""Application to visualize the fractal of Mandelbrot and julia."""
__all__ = [
    "ModuloColoration",
    "Fractale",
    "Julia",
    "Mandelbrot",
    "FractaleManager"
]

__version__ = "0.0.3"
__author__ = "Dashstrom"


from .model import (
    ModuloColoration,
    Fractale,
    Julia,
    Mandelbrot,
    FractaleManager
)
