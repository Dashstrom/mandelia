import tkinter as tk
from tkinter.constants import NW, X, Y, BOTH, TRUE, W, LEFT
from typing import Optional

from PIL import Image, ImageTk

from .export import Export
from .widget import AdjustableInput, Output
from ..util import set_icon


class StateInteraction(tk.LabelFrame):
    """Interaction for state."""
    def __init__(self, master: Optional[tk.Misc]) -> None:
        """Instantiate StateInteraction."""
        super().__init__(master, text="Options", labelanchor=NW)

        self.actualization = tk.Button(self, text="Actualiser")
        self.reset = tk.Button(self, text="Réinitialiser")

        self.actualization.pack(pady=5, fill=X, padx=20)
        self.reset.pack(pady=5, fill=X, padx=20)


class FileInteraction(tk.LabelFrame):
    """Interaction for file."""
    def __init__(self, master: Optional[tk.Misc]) -> None:
        """Instantiate StateInteraction."""
        super().__init__(master, text="Fichier", labelanchor=NW)

        self.load = tk.Button(self, text="Charger")
        self.save = tk.Button(self, text="Enregistrer")
        self.export = tk.Button(self, text="Exporter")

        self.load.pack(pady=5, fill=X, padx=20)
        self.save.pack(pady=5, fill=X, padx=20)
        self.export.pack(pady=5, fill=X, padx=20)


class ColorInteraction(tk.LabelFrame):
    """Interaction for color."""
    def __init__(self, master: Optional[tk.Misc]) -> None:
        """Instantiate ColorInteraction."""
        super().__init__(master, text="Couleur", labelanchor=NW)

        self.red = AdjustableInput(self, "Rouge", 0, 3, 20)
        self.green = AdjustableInput(self, "Vert", 0, 1, 20)
        self.blue = AdjustableInput(self, "Bleu", 0, 10, 20)
        self.button = tk.Button(self, text="Surprends-moi (⁄ ⁄•⁄ω⁄•⁄ ⁄)")

        self.red.pack(anchor=W, fill=X)
        self.green.pack(anchor=W, fill=X)
        self.blue.pack(anchor=W, fill=X)
        self.button.pack(pady=5, fill=X, padx=20)


class IterationInteraction(tk.LabelFrame):
    """Interaction for iteration."""
    def __init__(self, master: Optional[tk.Misc]) -> None:
        """Instantiate IterationInteraction."""
        super().__init__(master, text="Iterations", labelanchor=NW)

        self.max = AdjustableInput(self, "Max", 100, 2_000, 10_000)
        self.sum = Output(self, "Total", 0)
        self.per_pixel = Output(self, "Par pixel", 0)

        self.max.pack(anchor=W, fill=X)
        self.sum.pack(anchor=W, fill=X)
        self.per_pixel.pack(anchor=W, fill=X)


class PositioningInteraction(tk.LabelFrame):
    """Interaction for positioning."""
    def __init__(self, master: Optional[tk.Misc]) -> None:
        """Instantiate PositioningInteraction."""
        super().__init__(master, text="Positionnement", labelanchor=NW)

        self.zoom = Output(self, text="Zoom", default=1)
        self.real = Output(self, text="Re", default=0)
        self.imaginary = Output(self, text="Im", default=0)

        self.zoom.pack(anchor=W, fill=X)
        self.real.pack(anchor=W, fill=X)
        self.imaginary.pack(anchor=W, fill=X)


class MainInteraction(tk.Frame):
    """Manage all interaction."""
    def __init__(self, master: Optional[tk.Misc]) -> None:
        """Instantiate MainInteraction."""
        super().__init__(master)
        self._export_callback = None
        self.action = StateInteraction(self)
        self.file = FileInteraction(self)
        self.color = ColorInteraction(self)
        self.iteration = IterationInteraction(self)
        self.positioning = PositioningInteraction(self)

        self.action.pack(fill=X, padx=10)
        self.file.pack(fill=X, pady=5, padx=10)
        self.color.pack(fill=X, pady=5, padx=10)
        self.iteration.pack(fill=X, pady=5, padx=10)
        self.positioning.pack(fill=X, pady=5, padx=10)

        self.file.export.configure(command=self.open_export)

    def bind_export(self, func):
        """Set function to call on export."""
        self._export_callback = func

    def open_export(self):
        """Ask for export."""
        export = Export(self)
        if export.data and hasattr(self, "_export_callback"):
            self._export_callback(export.data)


class View(tk.Tk):
    """Main view."""
    def __init__(self) -> None:
        """Instantiate View."""
        super().__init__()
        self.resizable(width=True, height=True)
        self.title("Mandelia")
        self.configure(bg='black')
        self.minsize(800, 620)
        self.geometry("800x620")
        self._export_callback = None
        self.__image: Optional[Image.Image] = None
        self.__image_tk: Optional[ImageTk.PhotoImage] = None
        self.__image2: Optional[Image.Image] = None
        self.__image_tk2: Optional[ImageTk.PhotoImage] = None
        self.active = True
        self.__index: Optional[int] = None
        self.__index2: Optional[int] = None
        set_icon(self)
        self.visualization = tk.Canvas(self, width=600, height=600, bd=0,
                                       highlightthickness=0, bg="black")
        self.interaction = MainInteraction(self)
        self.interaction.pack(side=LEFT, fill=Y)
        self.visualization.pack(fill=BOTH, expand=TRUE)

    def set_image(self, image: Image.Image):
        """Set the main image."""
        self.__image = image
        self.__image_tk = ImageTk.PhotoImage(self.__image)
        if self.__index is not None:
            self.visualization.delete(self.__index)
        self.__index = self.visualization.create_image(
            0, 0, image=self.__image_tk, anchor=NW)
        self.visualization.tag_lower(self.__index)
        self.update_idletasks()

    def set_2nd_image(self, image: Image.Image):
        """Set the second image."""
        self.__image2 = image
        self.__image_tk2 = ImageTk.PhotoImage(self.__image2)
        if self.__index2 is not None:
            self.visualization.delete(self.__index2)
        self.__index2 = self.visualization.create_image(
            0, 0, image=self.__image_tk2, anchor=NW)
        self.visualization.tag_raise(self.__index2)
        self.update_idletasks()

    @property
    def width(self):
        """Get width of visualization canvas."""
        return self.visualization.winfo_width()

    @property
    def height(self):
        """Get height of visualization canvas."""
        return self.visualization.winfo_height()

    @property
    def red(self):
        """Get red color variable."""
        return self.interaction.color.red.var

    @property
    def green(self):
        """Get green color variable."""
        return self.interaction.color.green.var

    @property
    def blue(self):
        """Get blue color variable."""
        return self.interaction.color.blue.var
