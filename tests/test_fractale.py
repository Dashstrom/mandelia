from unittest import TestCase
from mandelia.model import Mandelbrot, Julia, ModuloColoration


class TestMandelbrot(TestCase):

    def setUp(self) -> None:
        self.color = ModuloColoration(9, 2, 3)
        self.mandelbrot = Mandelbrot(self.color, width=256, height=128)

    def test_image(self) -> None:
        img = self.mandelbrot.image()
        w, h = img.size
        self.assertEqual(w, 256)
        self.assertEqual(h, 128)


class TestJulia(TestCase):

    def setUp(self) -> None:
        self.color = ModuloColoration(9, 2, 3)
        self.julia = Julia(self.color, width=256, height=128)

    def test_image(self) -> None:
        img = self.julia.image()
        w, h = img.size
        self.assertEqual(w, 256)
        self.assertEqual(h, 128)
