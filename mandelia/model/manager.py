"""Manage fractale mandelbrot and julia."""
import sys
from typing import Optional, Callable, Tuple

from PIL import Image

from .fractale import (
    Mandelbrot,
    Julia,
    Fractale,
    ModuloColoration
)


if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


class DataExport(TypedDict):
    """Represent a metadata of media export."""
    path: str
    ext: str
    width: int
    height: int
    compression: int
    fps: int
    speed: int


RATIO = 3
ProgressHandler = Callable[[float, Image.Image], None]


class FractaleManager:
    """Manage fractale mandelbrot and julia."""
    def __init__(self, width: int, height: int) -> None:
        """Instantiate FractaleManager."""
        self.__coloration = ModuloColoration(3, 1, 10)
        self.__mandelbrot = Mandelbrot(self.__coloration,
                                       width=width,
                                       height=height)
        self.__julia = Julia(self.__coloration,
                             width=int(width / RATIO),
                             height=int(height / RATIO))
        self.first: Fractale = self.__mandelbrot
        self.second: Fractale = self.__julia

    def resize(self, width: int, height: int) -> None:
        """Resize 2 fractals."""
        self.first.resize(width, height)
        self.second.resize(int(width / RATIO), int(height / RATIO))

    def images(self) -> Tuple[Image.Image, Image.Image]:
        """Return 2 fractals docs."""
        return self.first.image(), self.second.image()

    def drop(
            self,
            data: DataExport,
            handler_progress: Optional[ProgressHandler] = None
    ) -> None:
        """Run a video from top to actual point."""
        self.first.drop(data, handler_progress)

    def swap(self) -> None:
        """Swap first with the second fractal."""
        w, h = self.first.width, self.first.height
        self.first.resize(int(w / RATIO), int(h / RATIO))
        self.second.resize(w, h)
        self.first, self.second = self.second, self.first

    def is_mandelbrot_first(self) -> bool:
        """Return if The first fractal is Mandelbrot."""
        return self.first == self.__mandelbrot

    def motion(self, x: int, y: int) -> None:
        """Set C complex of Julia."""
        if self.is_mandelbrot_first():
            r = self.__mandelbrot.real_at_x(x)
            i = self.__mandelbrot.imaginary_at_y(y)
            self.__julia.set_c_r(r)
            self.__julia.set_c_i(i)

    def save_size(self) -> int:
        """Return the size of save."""
        return 1 + self.__mandelbrot.bytes_size() + self.__julia.bytes_size()

    def save(self, path: str) -> None:
        """Save state of manager."""
        with open(path, "wb") as file:
            file.write(self.to_bytes())

    def to_bytes(self) -> bytes:
        """Convert the state of manager to bytes."""
        data = b"\x01" if self.is_mandelbrot_first() else b"\x00"
        data += self.__mandelbrot.to_bytes()
        data += self.__julia.to_bytes()
        return data

    def load(self, path: str) -> None:
        """Load fractals from path."""
        try:
            with open(path, "rb") as file:
                data = file.read(self.save_size() + 1)
        except FileNotFoundError:
            raise FileNotFoundError(
                "Le fichier {!r} n'a pas pu être trouvé".format(path)
            ) from None
        self.from_bytes(data)

    def from_bytes(self, data: bytes) -> None:
        """Load manager from bytes."""
        if len(data) != self.save_size():
            raise ValueError(
                "Mauvais type de fichier.\n"
                "Ca taille ne correspond pas au format d'un fichier .mbc")
        temp = self.to_bytes()
        try:
            is_mandelbrot = data[0]
            if is_mandelbrot != self.is_mandelbrot_first():
                self.swap()
            mandelbrot_data = data[1:36]
            julia_data = data[36:]
            self.__julia.from_bytes(julia_data)
            self.__mandelbrot.from_bytes(mandelbrot_data)
        except Exception as err:
            self.from_bytes(temp)  # need to return in previous state
            raise err

    def zoom(self, x: int, y: int, power: float) -> None:
        """Zoom in Image."""
        self.first.zoom(x, y, power)

    @property
    def pixel_size(self) -> float:
        """Get pixel size."""
        return self.first.pixel_size

    @property
    def iterations(self) -> int:
        """Get max iterations."""
        return self.first.iterations

    @iterations.setter
    def iterations(self, iterations: int) -> None:
        """Set max iterations."""
        self.first.set_iterations(iterations)
        self.second.set_iterations(iterations)

    def color(self, r: int, g: int, b: int) -> None:
        """Set RGB color."""
        color = self.__coloration
        color.r = r
        color.g = g
        color.b = b

    @property
    def rgb(self) -> Tuple[int, int, int]:
        """Get RGB color."""
        color = self.__coloration
        return color.r, color.g, color.b

    @property
    def real(self) -> float:
        """Z Real part of Mandelbrot."""
        return self.__mandelbrot.real

    @property
    def imaginary(self) -> float:
        """Z Imaginary part of Mandelbrot."""
        return self.__mandelbrot.imaginary

    @property
    def iter_sum(self) -> int:
        """Total of all iterations."""
        return self.first.iterations_sum()

    @property
    def iter_pixel(self) -> float:
        """IterationInteraction per pixel. If not pixel return 0."""
        return self.first.iterations_per_pixel()

    @property
    def iter_second(self) -> float:
        """Iterations per seconds."""
        return 0

    def reset(self) -> None:
        """Reset fractals."""
        self.__mandelbrot.reset()
        self.__julia.reset()
