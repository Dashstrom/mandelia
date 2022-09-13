"""Model module."""
from .fractale import Fractale, Julia, Mandelbrot, ModuloColoration
from .manager import DataExport, FractaleManager

__all__ = [
    "ModuloColoration", "Fractale", "Julia",
    "Mandelbrot", "FractaleManager", "DataExport"
]
