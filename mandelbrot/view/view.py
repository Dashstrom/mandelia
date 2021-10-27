from tkinter import LabelFrame, Misc, Button, Frame, Canvas, Tk
from tkinter.constants import NW, X, Y, BOTH, TRUE, W, LEFT
from typing import Optional

from PIL import Image, ImageTk

from mandelbrot.utils import resource_path
from mandelbrot.view.base import AdjustableInput, Output
from mandelbrot.view.export import Export


class Action(LabelFrame):
    def __init__(self, master: Optional[Misc]) -> None:
        super().__init__(master, text="Action", labelanchor=NW)

        self.actualization = Button(self, text="Actualiser")
        self.reset = Button(self, text="Réinitialiser")

        self.actualization.pack(pady=5, fill=X, padx=20)
        self.reset.pack(pady=5, fill=X, padx=20)


class File(LabelFrame):
    def __init__(self, master: Optional[Misc]) -> None:
        super().__init__(master, text="Fichier", labelanchor=NW)

        self.load = Button(self, text="Charger")
        self.save = Button(self, text="Enregistrer")
        self.export = Button(self, text="Exporter")

        self.load.pack(pady=5, fill=X, padx=20)
        self.save.pack(pady=5, fill=X, padx=20)
        self.export.pack(pady=5, fill=X, padx=20)


class Color(LabelFrame):
    def __init__(self, master: Optional[Misc]) -> None:
        super().__init__(master, text="Couleur", labelanchor=NW)

        self.red = AdjustableInput(self, "Rouge", 0, 3, 20)
        self.green = AdjustableInput(self, "Vert", 0, 1, 20)
        self.blue = AdjustableInput(self, "Bleu", 0, 10, 20)
        self.button = Button(self, text="Surprends-moi (⁄ ⁄•⁄ω⁄•⁄ ⁄)")

        self.red.pack(anchor=W, fill=X)
        self.green.pack(anchor=W, fill=X)
        self.blue.pack(anchor=W, fill=X)
        self.button.pack(pady=5, fill=X, padx=20)


class Iteration(LabelFrame):
    def __init__(self, master: Optional[Misc]) -> None:
        super().__init__(master, text="Iteration", labelanchor=NW)

        self.max = AdjustableInput(self, "Max", 100, 2_000, 10_000)
        self.sum = Output(self, "Total", 0)
        self.per_pixel = Output(self, "Par pixel", 0)

        self.max.pack(anchor=W, fill=X)
        self.sum.pack(anchor=W, fill=X)
        self.per_pixel.pack(anchor=W, fill=X)


class Positioning(LabelFrame):
    def __init__(self, master: Optional[Misc]) -> None:
        super().__init__(master, text="Positionnement", labelanchor=NW)

        self.zoom = Output(self, text="Zoom", default=1)
        self.real = Output(self, text="Re", default=0)
        self.imaginary = Output(self, text="Im", default=0)

        self.zoom.pack(anchor=W, fill=X)
        self.real.pack(anchor=W, fill=X)
        self.imaginary.pack(anchor=W, fill=X)


class View(Tk):
    def __init__(self) -> None:
        super().__init__()
        self.resizable(width=True, height=True)
        self.title("Mandelbrot")
        self.configure(bg='black')
        self.minsize(800, 620)
        self.geometry("800x620")
        self._export_callback = None
        self.__image = None
        self.__image_tk = None
        self.__image2 = None
        self.__image_tk2 = None
        self.active = True
        self.__index = None
        self.__index2 = None
        try:
            self.iconbitmap(resource_path("logo.ico"))
        except Exception as err:
            print(err)

        self.canvas = Canvas(self, width=600, height=600, bd=0,
                             highlightthickness=0, bg="black")
        self.aside = Frame(self)
        self.action = Action(self.aside)
        self.file = File(self.aside)
        self.color = Color(self.aside)
        self.iteration = Iteration(self.aside)
        self.positioning = Positioning(self.aside)

        self.aside.pack(side=LEFT, fill=Y)
        self.canvas.pack(fill=BOTH, expand=TRUE)
        self.action.pack(fill=X, padx=10)
        self.file.pack(fill=X, pady=5, padx=10)
        self.color.pack(fill=X, pady=5, padx=10)
        self.iteration.pack(fill=X, pady=5, padx=10)
        self.positioning.pack(fill=X, pady=5, padx=10)

        self.file.export.configure(command=self.open_export)

    def bind_export(self, func):
        self._export_callback = func

    def open_export(self):
        export = Export(self)
        if export.data and hasattr(self, "_export_callback"):
            self._export_callback(export.data)

    def set_image(self, image: Image.Image):
        self.__image = image
        self.__image_tk = ImageTk.PhotoImage(self.__image)
        if self.__index is not None:
            self.canvas.delete(self.__index)
        self.__index = self.canvas.create_image(
            0, 0, image=self.__image_tk, anchor=NW)
        self.canvas.tag_lower(self.__index)
        self.update_idletasks()

    def set_2nd_image(self, image: Image.Image):
        self.__image2 = image
        self.__image_tk2 = ImageTk.PhotoImage(self.__image2)
        if self.__index2 is not None:
            self.canvas.delete(self.__index2)
        self.__index2 = self.canvas.create_image(
            0, 0, image=self.__image_tk2, anchor=NW)
        self.canvas.tag_raise(self.__index2)
        self.update_idletasks()

    @property
    def width(self):
        return self.canvas.winfo_width()

    @property
    def height(self):
        return self.canvas.winfo_height()

    @property
    def red(self):
        return self.color.red.var

    @property
    def green(self):
        return self.color.green.var

    @property
    def blue(self):
        return self.color.blue.var
