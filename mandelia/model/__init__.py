"""Model module."""
from .fractale import ModuloColoration, Fractale, Julia, Mandelbrot
from .manager import FractaleManager, DataExport


__all__ = [
    "ModuloColoration", "Fractale", "Julia",
    "Mandelbrot", "FractaleManager", "DataExport"
]
