from math import ceil
import tkinter as tk
from tkinter import ttk
from tkinter.constants import NW, X, HORIZONTAL, BOTTOM
from typing import Optional

from PIL import Image, ImageTk

from ..util import set_icon


class Wait(tk.Toplevel):
    """Window for preview."""
    def __init__(self, view: tk.Misc) -> None:
        """Instantiate preview window."""
        super().__init__(view)
        self.resizable(width=False, height=False)
        self.title("Opération lente")
        self.root = view
        self.configure()
        self.geometry("300x300")
        set_icon(self)
        self.__image: Optional[Image.Image] = None
        self.__image_tk: Optional[ImageTk.PhotoImage] = None
        self.__index: Optional[int] = None
        self.var = tk.IntVar(self, 0)

        self.label = tk.Label(self, text="Une opération lente est en cours")
        self.canvas = tk.Canvas(self, width=200, height=200, bd=0,
                                highlightthickness=0, bg="#c8c8c8")
        self.progressbar = ttk.Progressbar(
            self, variable=self.var, orient=HORIZONTAL, value=0, maximum=100
        )
        self.cancel = tk.Button(self, text="Annuler",
                                command=self.destroy, width=20)

        self.label.pack(fill=X, padx=20)
        self.canvas.pack()
        self.progressbar.pack(fill=X, side=BOTTOM)
        self.cancel.pack(pady=10)

        # self.take_control()

    def done(self):
        """Alias for destroy."""
        self.destroy()
        self.update()

    def set_preview(self, image: Image.Image):
        """Set image to preview."""
        w, h = image.size
        ratio_w = w / 200
        ratio_h = h / 200
        ratio = max(ratio_h, ratio_w)
        img_w = ceil(w / ratio)
        img_h = ceil(h / ratio)
        self.__image = image.resize((img_w, img_h))
        self.__image_tk = ImageTk.PhotoImage(self.__image)
        if self.__index is not None:
            self.canvas.delete(self.__index)
        self.__index = self.canvas.create_image(
            100 - img_w / 2, 100 - img_h / 2, image=self.__image_tk, anchor=NW)
        self.canvas.tag_lower(self.__index)
        self.update()

    def progress(self, percent: float) -> None:
        """Update progress bar."""
        if ceil(percent * 100) != self.var.get():
            self.var.set(ceil(percent * 100))
            self.root.update()
