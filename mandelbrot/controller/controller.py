from contextlib import contextmanager
from math import log
from random import randint
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.messagebox import showerror, showinfo
from traceback import print_exc

import cv2
import numpy as np
from PIL import Image

from ..model.manager import FractaleManager
from ..view.view import View
from ..view.wait import Wait
from ..util import logger, stat_file


class Controller:
    """General controller."""
    def __init__(self, path: str = None) -> None:
        """Instantiate Controller."""
        with self.lock_update():
            view = self.view = View()
            view.update()
            self.manager = FractaleManager(view.width, view.height)
            self.__ignore_update = False

            interaction = view.interaction
            interaction.action.actualization.config(command=self.on_actualization)
            interaction.color.button.config(command=self.on_random_color)
            interaction.action.reset.config(command=self.on_reset)
            interaction.file.save.config(command=self.on_save)
            interaction.file.load.config(command=self.on_load)
            interaction.bind_export(self.on_export)
            interaction.iteration.max.var.trace(
                "w", lambda *_: self.on_iteration_max())

            view.visualization.bind("<MouseWheel>", self.on_wheel)
            view.visualization.bind("<Button-4>", self.on_right_click)
            view.visualization.bind("<Button-5>", self.on_left_click)
            
            view.visualization.bind("<Configure>", self.on_resize)
            view.visualization.bind('<Motion>', self.on_motion)
            view.visualization.bind("<Button>", self.touchpad_events)
            view.visualization.bind('<Double-1>', lambda *_: self.on_swap())
            view.red.trace("w", lambda *_: self.on_color())
            view.green.trace("w", lambda *_: self.on_color())
            view.blue.trace("w", lambda *_: self.on_color())
        if path is not None:
            if not self.load_configuration(path):
                self.update()
        else:
            self.update()
        self.view.mainloop()

    def __repr__(self) -> str:
        """Represent a Controller."""
        name = self.__class__.__name__
        return f"<{name} locked_update={self.locked_update}>"
    
    def touchpad_events(self, event):
        print(event)
        if event.num==4:
            self.xview_scroll(-10, "units")
            return "break"
        elif event.num==5:
            self.xview_scroll(10, "units")
            return "break"

    @logger
    def on_swap(self):
        """Handle swap between julia and mandelbrot."""
        self.manager.swap()
        img1, img2 = self.manager.images()
        self.view.set_image(img1)
        self.view.set_2nd_image(img2)
        self.update()

    @logger
    def _end_export(self, path: str):
        """Show information about file."""
        showinfo("Exporter", f"Exportation réussi\n{stat_file(path)}")

    @logger
    def on_export(self, data):
        """Handle export."""
        print(data)
        p: str = data["path"].lower()
        width, height = data["width"], data["height"]
        fractale = self.manager.first
        try:
            open(data["path"], "a")
        except OSError:
            print("invalid path")
            return
        if p.endswith((".png", ".pns", ".jpeg", ".jpe", ".jpeg")):
            img: Image.Image = fractale.image_at_size(width, height)
            img.save(data["path"], quality=data["compression"])
            self._end_export(data["path"])
        elif p.endswith((".gif", ".mp4")):
            wait = Wait(self.view)
            data_frac = fractale.to_bytes()
            pixel_size = fractale.pixel_size
            speed = data["speed"] / 10
            fractale.top()
            fractale.resize(width, height)
            img = fractale.image()
            wait.set_preview(img)
            multi = 1 + speed / data["fps"]

            print("zoom of :", multi)
            start_pixel_size = fractale.pixel_size
            s = log(start_pixel_size, multi)
            e = log(pixel_size, multi)

            def iterate_images():
                while fractale.pixel_size > pixel_size:
                    fractale.middle_zoom(multi)
                    p = log(fractale.pixel_size, multi)
                    prog = (p - s) / (e - s)
                    wait.progress(max(0.0, min(prog, 1.0)))
                    print(f"({p} - {s}) / ({e} - {s}) = {prog}")
                    img = fractale.image()
                    wait.set_preview(img)
                    yield img

            if p.endswith(".gif"):
                img.save(data["path"], fromat='GIF', save_all=True,
                         append_images=list(iterate_images()),
                         optimize=True, duration=int(1000 / data["fps"]),
                         loop=0, palette=Image.ADAPTIVE, disposal=1)
                self._end_export(data["path"])
            else:
                codec = cv2.VideoWriter_fourcc(*'mp4v')
                video = cv2.VideoWriter(data["path"], codec, data["fps"],
                                        (width, height))
                video.write(cv2.cvtColor(np.array(img),  # type: ignore
                                         cv2.COLOR_RGB2BGR))
                for frame in iterate_images():
                    video.write(cv2.cvtColor(np.array(frame),  # type: ignore
                                             cv2.COLOR_RGB2BGR))
                video.release()
                self._end_export(data["path"])
            fractale.resize(self.view.width, self.view.height)
            fractale.from_bytes(data_frac)

    def on_motion(self, event):
        """Handle mouse movement."""
        self.manager.motion(event.x, event.y)
        if self.manager.is_mandelbrot_first():
            img = self.manager.second.image()
            self.view.set_2nd_image(img)

    def load_configuration(self, path):
        """Load configuration with displayable error."""
        self.manager.load(path)
        self.update()
        self.update_colors()

    @contextmanager
    def lock_update(self):
        """Context manager for lock update for a short while."""
        self.__ignore_update = True
        yield
        self.__ignore_update = False

    @property
    def locked_update(self):
        """Return if update is locked."""
        return self.__ignore_update

    @logger
    def on_load(self):
        """Handle load of configuration."""
        path = askopenfilename(
            title="Charger la configuration",
            filetypes=[('Mandelbrot configuration Files', '.mbc')],
            initialfile="projet.mbc"
        )
        if path:
            self.load_configuration(path)

    @logger
    def on_save(self):
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
                         "Enregistrement réussi\n"
                         + stat_file(path))
            except PermissionError:
                showerror("Enregistrer la configuration",
                          "Le fichier n'a pas pu être ouvert")
            except OSError:
                showerror("Enregistrer la configuration",
                          "Une erreur est survenue")
                print_exc()

    def on_wheel(self, event):
        """Handle wheel bearing for zoom."""
        self.zoom(event.x, event.y, 2 if event.delta > 0 else 0.5)
    
    def on_right_click(self, event):
        self.zoom(event.x, event.y, 2)
    
    def on_left_click(self, event):
        self.zoom(event.x, event.y, 0.5)

    @logger
    def zoom(self, x, y, power):
        self.manager.zoom(x, y, power)
        self.update()

    @logger
    def on_iteration_max(self):
        """Handle change of max iterations."""
        self.manager.iterations = self.view.interaction.iteration.max.var.get()

    @logger
    def on_color(self):
        """Handle color changes."""
        if self.locked_update:
            return
        self.manager.color(
            self.view.red.get(),
            self.view.green.get(),
            self.view.blue.get()
        )
        self.update_colors()
        self.update()

    @logger
    def update(self):
        """Update images."""
        if self.locked_update:
            return
        manager = self.manager
        view = self.view
        with self.lock_update():
            interaction = view.interaction
            interaction.positioning.real.var.set(manager.real)
            interaction.positioning.imaginary.var.set(manager.imaginary)
            interaction.positioning.zoom.var.set(manager.pixel_size)
            interaction.iteration.max.var.set(manager.iterations)
            interaction.iteration.sum.var.set(f"{manager.iter_sum} i")
            interaction.iteration.per_pixel.var.set(f"{manager.iter_pixel:.2f} i/pxl")
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
    def on_resize(self, event) -> None:
        """Handle window resize."""
        self.manager.resize(event.width, event.height)
        self.view.set_2nd_image(self.manager.second.image())
        self.update()

    @logger
    def on_actualization(self):
        """Handle actualization button."""
        self.manager.resize(self.view.width, self.view.height)
        self.update()

    @logger
    def on_reset(self):
        """Handle reset button."""
        self.manager.reset()
        self.view.set_2nd_image(self.manager.second.image())
        self.update()
