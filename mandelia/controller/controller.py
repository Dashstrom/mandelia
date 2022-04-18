"""Controller of every view."""
import tkinter as tk
from contextlib import contextmanager
from random import randint
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.messagebox import showerror, showinfo
from traceback import print_exc
from typing import Optional, Generator
from PIL import Image

from mandelia.view.export import DataExport

from ..model.manager import FractaleManager
from ..view.view import View
from ..view.wait import Wait
from ..util import logger, stat_file


class Controller:
    """General controller."""

    def __init__(self, path: Optional[str] = None) -> None:
        """Instantiate Controller."""
        with self.lock_update():
            view = self.view = View()
            view.update()
            self.manager = FractaleManager(view.width, view.height)
            self.__ignore_update = False
            self.__wait: Optional[Wait] = None

            interaction = view.interaction
            interaction.action.actualization.config(
                command=self.on_actualization)
            interaction.color.button.config(command=self.on_random_color)
            interaction.action.reset.config(command=self.on_reset)
            interaction.file.save.config(command=self.on_save)
            interaction.file.load.config(command=self.on_load)
            interaction.bind_export(self.on_export)
            interaction.iteration.max.var.trace_add(
                "write", self.on_iteration_max
            )

            view.visualization.bind("<MouseWheel>", self.on_wheel)
            view.visualization.bind("<Button-4>", self.on_right_click)
            view.visualization.bind("<Button-5>", self.on_left_click)

            view.visualization.bind("<Configure>", self.on_resize)
            view.visualization.bind('<Motion>', self.on_motion)
            view.visualization.bind('<Double-1>', self.on_swap)
            view.red.trace_add("write", lambda *_: self.on_color())
            view.green.trace_add("write", lambda *_: self.on_color())
            view.blue.trace_add("write", lambda *_: self.on_color())
        if path is not None:
            self.load_configuration(path)
        else:
            self.update()
        self.view.mainloop()

    def __repr__(self) -> str:
        """Represent a Controller."""
        name = self.__class__.__name__
        return "<{} locked_update={}>".format(name, self.locked_update)

    @logger
    def on_swap(self, event):
        # type: (tk.Event[tk.Canvas]) -> None
        """Handle swap between julia and mandelbrot."""
        self.manager.swap()
        img1, img2 = self.manager.images()
        self.view.set_image(img1)
        self.view.set_2nd_image(img2)
        self.update()

    @logger
    def on_export(self, data: DataExport) -> None:
        """Handle export."""
        if self.__wait is not None:
            showerror("Opération en cours",
                      "Un export est déjà en cours, "
                      "veuillez la fermer pour exporter de nouveau")
            return
        path = data["path"]
        ext = data["ext"]
        if ext in ("gif", "mp4"):
            wait = self.__wait = Wait(self.view)

            def handler_progress(progress: float, image: Image.Image) -> None:
                wait.progress(progress)
                wait.set_preview(image)
                if progress == 1:
                    wait.done()
                self.view.update()
        else:
            def handler_progress(progress: float, image: Image.Image) -> None:
                pass

        try:
            self.manager.drop(data, handler_progress)
            showinfo("Exporter", "Exportation réussi\n" + stat_file(path))
        except tk.TclError:
            showerror("Opération annulée", "L'opération a été annulée")
        finally:
            self.__wait = None
        self.view.update()

    def on_motion(self, event):
        # type: (tk.Event[tk.Canvas]) -> None
        """Handle mouse movement."""
        self.manager.motion(event.x, event.y)
        if self.manager.is_mandelbrot_first():
            img = self.manager.second.image()
            self.view.set_2nd_image(img)

    def load_configuration(self, path: str) -> None:
        """Load configuration with displayable error."""
        self.manager.load(path)
        self.update()
        self.update_colors()

    @contextmanager
    def lock_update(self) -> Generator[None, None, None]:
        """Context manager for lock update for a short while."""
        self.__ignore_update = True
        yield
        self.__ignore_update = False

    @property
    def locked_update(self) -> bool:
        """Return if update is locked."""
        return self.__ignore_update

    @logger
    def on_load(self) -> None:
        """Handle load of configuration."""
        path = askopenfilename(
            title="Charger la configuration",
            filetypes=[('Mandelbrot configuration Files', '.mbc')],
            initialfile="projet.mbc"
        )
        if path:
            self.load_configuration(path)

    @logger
    def on_save(self) -> None:
        """Handle save of configuration."""
        path = asksaveasfilename(
            title="Enregistrer la configuration",
            filetypes=[('Mandelbrot configuration Files', '.mbc')],
            initialfile="projet.mbc"
        )
        if path:
            try:
                self.manager.save(path)
                showinfo("Enregistrer la configuration",
                         "Enregistrement réussi\n" + stat_file(path))
            except PermissionError:
                showerror("Enregistrer la configuration",
                          "Le fichier n'a pas pu être ouvert")
            except OSError:
                showerror("Enregistrer la configuration",
                          "Une erreur est survenue")
                print_exc()

    def on_wheel(self, event):
        # type: (tk.Event[tk.Canvas]) -> None
        """Handle wheel bearing for zoom."""
        self.zoom(event.x, event.y, 2 if event.delta > 0 else 0.5)

    def on_right_click(self, event):
        # type: (tk.Event[tk.Canvas]) -> None
        """Handle right click."""
        self.zoom(event.x, event.y, 2)

    def on_left_click(self, event):
        # type: (tk.Event[tk.Canvas]) -> None
        """Handle left click."""
        self.zoom(event.x, event.y, 0.5)

    @logger
    def zoom(self, x: int, y: int, power: float) -> None:
        """Zoom in actual fractale."""
        self.manager.zoom(x, y, power)
        self.update()

    @logger
    def on_iteration_max(self, name: str, index: str, mode: str) -> None:
        """Handle change of max iterations."""
        iterations = int(self.view.interaction.iteration.max.var.get())
        self.manager.iterations = iterations

    @logger
    def on_color(self) -> None:
        """Handle color changes."""
        if self.locked_update:
            return
        self.manager.color(
            int(self.view.red.get()),
            int(self.view.green.get()),
            int(self.view.blue.get())
        )
        self.update_colors()
        self.update()

    @logger
    def update(self) -> None:
        """Update images."""
        if self.locked_update:
            return
        manager = self.manager
        view = self.view
        with self.lock_update():
            interaction = view.interaction
            interaction.positioning.real.var.set(str(manager.real))
            interaction.positioning.imaginary.var.set(str(manager.imaginary))
            interaction.positioning.zoom.var.set(str(manager.pixel_size))
            interaction.iteration.max.var.set(manager.iterations)
            interaction.iteration.sum.var.set("{} i".format(manager.iter_sum))
            interaction.iteration.per_pixel.var.set(
                "{:.2f} i/pxl".format(manager.iter_pixel))
            img = manager.first.image()
            self.view.set_image(img)

    @logger
    def on_random_color(self) -> None:
        """Handle random color button pressed."""
        rgb = [randint(0, 6) + randint(0, 6) + randint(0, 4) for _ in range(3)]
        self.manager.color(*rgb)
        self.update_colors()
        self.update()

    def update_colors(self) -> None:
        """Update colors."""
        with self.lock_update():
            r, g, b = self.manager.rgb
            self.view.red.set(r)
            self.view.green.set(g)
            self.view.blue.set(b)
            self.view.set_image(self.manager.first.image())
            self.view.set_2nd_image(self.manager.second.image())

    @logger
    def on_resize(self, event):
        # type: (tk.Event[tk.Canvas]) -> None
        """Handle window resize."""
        self.manager.resize(event.width, event.height)
        self.view.set_2nd_image(self.manager.second.image())
        self.update()

    @logger
    def on_actualization(self) -> None:
        """Handle actualization button."""
        self.manager.resize(self.view.width, self.view.height)
        self.update()

    @logger
    def on_reset(self) -> None:
        """Handle reset button."""
        self.manager.reset()
        self.view.set_2nd_image(self.manager.second.image())
        self.update()
