from mandelbrot.view.base import AdjustableInput
from tkinter import *
from typing import Any, Dict, Optional
from mandelbrot.utils import resource_path
from tkinter.filedialog import asksaveasfilename


class Export(Toplevel):
    def __init__(self, view: Optional[Misc]) -> None:
        super().__init__(view)
        self.resizable(width=False, height=False)
        self.title("Exporter")
        self.root = view
        self.configure()
        self.geometry("300x300")
        try:
            self.iconbitmap(resource_path("logo.ico"))
        except Exception as err:
            print(err)
        self.data: Dict[str, Any] = {}
        self.format = LabelFrame(self, text="Format", labelanchor=NW)
        values = ['PNG', 'GIF', 'MP4']
        self.format_var = StringVar(self, values[0])
        self.formats = {}
        for val in values:
            self.formats[val] = Radiobutton(self.format, text=val, width=9,
                                            indicatoron=FALSE, value=val,
                                            variable=self.format_var)
        self.details = LabelFrame(self, text="Détails", labelanchor=NW)
        self.fps = AdjustableInput(self.details, "FPS", 5, 24, 60)
        self.width = AdjustableInput(self.details, "Largeur", 128, 1920, 3840)
        self.height = AdjustableInput(self.details, "Hauteur", 128, 1080, 3840)
        self.compression = AdjustableInput(self.details, "Compression",
                                           10, 95, 100)
        self.speed = AdjustableInput(self.details, "Vitesse", 5, 10, 50)
        self.button = Button(self, text="Terminer", command=self.terminate)

        self.format_var.trace("w", lambda *_: self.disable_useless())
        self.disable_useless()

        self.format.pack(padx=5, pady=5, ipady=3, fill=X)
        self.formats["PNG"].pack(side=LEFT, padx=3, fill=X, expand=True)
        self.formats["GIF"].pack(side=LEFT, padx=0, fill=X, expand=True)
        self.formats["MP4"].pack(side=LEFT, padx=3, fill=X, expand=True)
        self.details.pack(padx=5, fill=X)
        self.width.pack(fill=X)
        self.height.pack(fill=X)
        self.compression.pack(fill=X)
        self.fps.pack(fill=X)
        self.speed.pack(fill=X)
        self.width.pack(fill=X)
        self.height.pack(fill=X)
        self.button.pack(fill=X, padx=20)

        self.take_control()

    def disable_useless(self):
        fmt = self.format_var.get()
        if fmt == "PNG":
            self.speed.disable()
            self.fps.disable()
        else:
            self.speed.enable()
            self.fps.enable()

    def terminate(self):
        fmt = self.format_var.get()
        filetypes = [('PNG', '*.PNG *.PNS')]
        filetypes.insert(0 if fmt == "GIF" else 1, ('GIF', '*.GIF'))
        filetypes.insert(0 if fmt == "MP4" else 2, ('MP4', '*.MP4'))
        filetypes.append(('JPG', '*.JPG *.JPEG *.JPE'))
        path = asksaveasfilename(title="Exporter",
                                 filetypes=filetypes,
                                 initialfile=f"mandelbrot.{fmt.lower()}")
        if path:
            self.data = {
                "path": path,
                "width": int(self.width.var.get()),
                "height": int(self.height.var.get()),
                "compression": int(self.compression.var.get()),
                "fps": int(self.fps.var.get()),
                "speed": int(self.speed.var.get())
            }
            self.destroy()

    def take_control(self):
        self.transient(self.root)
        self.grab_set()
        self.root.wait_window(self)
