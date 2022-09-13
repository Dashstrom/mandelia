"""Application to visualize the fractal of Mandelbrot and julia."""
__all__ = [
    "ModuloColoration",
    "Fractale",
    "Julia",
    "Mandelbrot",
    "FractaleManager"
]

__version__ = "0.0.4"
__author__ = "Dashstrom"


from .model import (Fractale, FractaleManager, Julia, Mandelbrot,
                    ModuloColoration)
