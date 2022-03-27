from typing import Optional, Callable

from PIL import Image

from .fractale import (
    Mandelbrot,
    Julia,
    Fractale,
    ModuloColoration
)

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

    def images(self) -> tuple[Image.Image, Image.Image]:
        """Return 2 fractals docs."""
        return self.first.image(), self.second.image()

    def drop(
            self,
            metadata: dict,
            handler_progress: Optional[ProgressHandler] = None
    ) -> None:
        # TODO better type
        return self.first.drop(metadata, handler_progress)

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

    def save_size(self):
        return 1 + self.__mandelbrot.bytes_size() + self.__julia.bytes_size()

    def save(self, path: str) -> None:
        with open(path, "wb") as file:
            file.write(self.to_bytes())

    def to_bytes(self) -> bytes:
        return (bytes([1 if self.is_mandelbrot_first() else 0])
                + self.__mandelbrot.to_bytes()
                + self.__julia.to_bytes())

    def load(self, path: str) -> None:
        """Load fractals from path."""
        try:
            with open(path, "rb") as file:
                data = file.read(self.save_size() + 1)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Le fichier {path!r} n'a pas pu être trouvé") from None
        self.from_bytes(data)

    def from_bytes(self, data: bytes):
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
        except Exception as e:
            self.from_bytes(temp)  # need to return in previous state
            raise e

    def zoom(self, x: int, y: int, power: float) -> None:
        """Zoom in Image."""
        self.first.zoom(x, y, power)

    @property
    def pixel_size(self):
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
        c = self.__coloration
        c.r = r
        c.g = g
        c.b = b

    @property
    def rgb(self) -> tuple[int, int, int]:
        """Get RGB color."""
        c = self.__coloration
        return c.r, c.g, c.b

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
