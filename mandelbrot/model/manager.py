from PIL import Image

from .fractale import (
    Mandelbrot,
    Julia,
    Fractale,
    ModuloColoration
)

RATIO = 3
SAVE_SIZE = 113


class FractaleManager:
    def __init__(self, width: int, height: int) -> None:
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
        """"""
        self.first.resize(width, height)
        self.second.resize(int(width / RATIO), int(height / RATIO))

    def images(self) -> tuple[Image.Image, Image.Image]:
        """Return 2 fractals docs."""
        return self.first.image(), self.second.image()

    def swap(self) -> None:
        """Swap first with the second fractal."""
        w, h = self.first.width, self.first.height
        self.first.resize(int(w / RATIO), int(h / RATIO))
        self.second.resize(w, h)
        self.first, self.second = self.second, self.first

    def is_mandelbrot_first(self) -> bool:
        """Return True if The first fractal is Mandelbrot."""
        return self.first == self.__mandelbrot

    def motion(self, x: int, y: int) -> None:
        """Set C complex of Julia."""
        if self.is_mandelbrot_first():
            r = self.__mandelbrot.real_at_x(x)
            i = self.__mandelbrot.imaginary_at_y(y)
            self.__julia.set_c_r(r)
            self.__julia.set_c_i(i)

    def save(self, path: str) -> None:
        with open(path, "wb") as file:
            bytes_ = bytes([1 if self.is_mandelbrot_first() else 0])
            bytes_ += self.__mandelbrot.to_bytes()
            bytes_ += self.__julia.to_bytes()
            file.write(bytes_)

    def load(self, path: str) -> None:
        """Load fractals from path."""
        with open(path, "rb") as path:
            data = path.read(SAVE_SIZE + 1)
        if len(data) != SAVE_SIZE:
            raise ValueError(
                f"File must contain {SAVE_SIZE} bytes , got {len(data)}")
        is_mandelbrot_flag = data[0]
        if is_mandelbrot_flag != self.is_mandelbrot_first():
            self.swap()
        mandelbrot_data = data[1:49]
        julia_data = data[49:]
        self.__julia.from_bytes(julia_data)
        self.__mandelbrot.from_bytes(mandelbrot_data)

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
        """Iteration per pixel. If not pixel return 0."""
        return self.first.iterations_per_pixel()

    @property
    def iter_second(self) -> float:
        """Iterations per seconds."""
        return 0

    def reset(self) -> None:
        """Reset fractals."""
        self.__mandelbrot.reset()
        self.__julia.reset()
