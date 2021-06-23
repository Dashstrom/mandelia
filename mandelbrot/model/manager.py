from mandelbrot.model.fractale import Mandelbrot, Julia, Fractale
from PIL import Image


RATIO = 3


class FractaleManager:
    def __init__(self, width: int, height: int) -> None:
        self.__mandelbrot = Mandelbrot(iterations=1_000,
                                       width=width,
                                       height=height)
        self.__julia = Julia(iterations=1_000,
                             width=int(width / RATIO),
                             height=int(height / RATIO))
        self.first: Fractale = self.__mandelbrot
        self.second: Fractale = self.__julia

    def resize(self, width: int, height: int) -> None:
        self.first.resize(width, height)
        self.second.resize(int(width/RATIO), int(height/RATIO))

    def images(self) -> tuple[Image.Image, Image.Image]:
        return self.first.image(), self.second.image()

    def swap(self) -> None:
        w, h = self.first.get_width(), self.first.get_height()
        self.first.resize(int(w/RATIO), int(h/RATIO))
        self.second.resize(w, h)
        self.first, self.second = self.second, self.first

    def is_mandelbrot_first(self) -> bool:
        return self.first == self.__mandelbrot

    def motion(self, x: int, y: int) -> None:
        if self.is_mandelbrot_first():
            r = self.__mandelbrot.real_at_x(x)
            i = self.__mandelbrot.imaginary_at_y(y)
            self.__julia.set_real(r)
            self.__julia.set_imaginary(i)

    def save(self, path: str) -> None:
        with open(path, "wb+") as file:
            file.write(self.__mandelbrot.data())

    def load(self, path: str) -> None:
        with open(path, "rb") as path:
            data = path.read(500)
        self.__mandelbrot.from_data(data)

    def set_zoom(self, x: int, y: int, power: float) -> None:
        self.first.zoom(x, y, power)

    def get_zoom(self) -> int:
        return self.first.get_zoom()

    @property
    def iteration_max(self) -> int:
        return self.first.get_iteration_max()

    @iteration_max.setter
    def iteration_max(self, max_iteration: int) -> None:
        self.first.set_iteration_max(max_iteration)
        self.second.set_iteration_max(max_iteration)

    def color(self, r: int, g: int, b: int) -> None:
        self.first.set_color(r, g, b)
        self.second.set_color(r, g, b)

    @property
    def rgb(self) -> tuple[int, int, int]:
        return self.first.rgb()

    @property
    def real(self) -> float:
        return self.__mandelbrot.get_real()

    @property
    def imaginary(self) -> float:
        return self.__mandelbrot.get_imaginary()

    @property
    def iter_sum(self) -> int:
        return self.first.iterations_sum()

    @property
    def iter_pixel(self) -> float:
        return self.first.iterations_per_pixel()

    @property
    def iter_second(self) -> float:
        return self.first.iterations_per_second()

    def reset(self) -> None:
        self.__mandelbrot.reset()
        self.__julia.reset()
