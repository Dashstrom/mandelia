from random import randint
from PIL import Image
from datetime import datetime
from contextlib import contextmanager
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.messagebox import showerror, showinfo
from traceback import print_exc
from math import log, floor

import numpy as np
import os
import cv2

from mandelbrot.model.manager import FractaleManager
from mandelbrot.view.view import View
from mandelbrot.view.wait import Wait


def logger(func):
    def wrapper(*args, **kwargs):
        str_args = ", ".join(f"{arg!r}" for arg in args)
        str_kwargs = ",".join(f"{k}={arg!r}" for k, arg in kwargs.items())
        str_params = ",".join(part for part in (str_args, str_kwargs) if part)
        print(f"[{datetime.now()}] Call {func.__qualname__}({str_params})")
        return func(*args, **kwargs)

    return wrapper


def call(func):
    return lambda *_: func()


def stat_file(path: str) -> str:
    size = os.path.getsize(path)
    echelle = floor(log(size, 1024))
    print(echelle)
    c = {0: "", 1: "k", 2: "M"}.get(echelle, "G")
    print(f"{size}/{1024 ** echelle}={size/(1024 ** echelle)}")
    return f"Chemin : \"{path}\"\nTaille : {size/(1024 ** echelle):.2f}{c}o"


class Controller:

    def __init__(self, path: str = None) -> None:
        with self.lock_update():
            self.view = View()
            self.view.update()
            self.manager = FractaleManager(self.view.width, self.view.height)
            self.__ignore_update = False
            self.view.action.actualization.config(
                command=self.on_actualization)
            self.view.color.button.config(command=self.on_random_color)
            self.view.action.reset.config(command=self.on_reset)
            self.view.file.save.config(command=self.on_save)
            self.view.file.load.config(command=self.on_load)
            self.view.canvas.bind("<MouseWheel>", self.on_zoom)
            self.view.canvas.bind("<Configure>", self.on_resize)
            self.view.canvas.bind('<Motion>', self.on_motion)
            self.view.canvas.bind('<Double-1>', call(self.on_swap))
            self.view.red.trace("w", call(self.on_color))
            self.view.green.trace("w", call(self.on_color))
            self.view.blue.trace("w", call(self.on_color))
            self.view.iteration.max.var.trace("w", call(self.on_iteration_max))
            self.view.bind_export(self.on_export)
        if path:
            if not self._load_file(path):
                self.update()
        else:
            self.update()
        self.view.mainloop()

    def __repr__(self) -> str:
        name = self.__class__.__name__
        return f"<{name} locked_update={self.locked_update}>"

    @logger
    def on_swap(self):
        self.manager.swap()
        img1, img2 = self.manager.images()
        self.view.set_image(img1)
        self.view.set_2nd_image(img2)
        self.update()

    @logger
    def _end_export(self, path: str):
        showinfo("Exporter",
                 "Exportation réussi\n"
                 + stat_file(path))

    @logger
    def start_export(self, path: str):
        size = os.path.getsize(path)
        showinfo("Exporter",
                 "Exportation réussi\n"
                 + stat_file(path))

    @logger
    def on_export(self, data):
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
                video = cv2.VideoWriter(data["path"], -1, data["fps"],
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
        self.manager.motion(event.x, event.y)
        if self.manager.is_mandelbrot_first():
            img = self.manager.second.image()
            self.view.set_2nd_image(img)

    def _load_file(self, path):
        try:
            self.manager.load(path)
            self.update()
            self.update_colors()
            return True
        except FileNotFoundError:
            showerror(
                "Charger la configuration",
                "Le fichier n'a pas pu être trouvé"
            )
        except ValueError:
            showerror(
                "Charger la configuration",
                "Mauvais type de fichier.\n"
                "Ca taille ne correspond pas au format d'un fichier .mbc"
            )
        except OSError:
            print_exc()
        return False

    @contextmanager
    def lock_update(self):
        self.__ignore_update = True
        yield
        self.__ignore_update = False

    @property
    def locked_update(self):
        return self.__ignore_update

    @logger
    def on_load(self):
        path = askopenfilename(
            title="Charger la configuration",
            filetypes=[('Mandelbrot configuration Files', '.mbc')],
            initialfile="projet.mbc"
        )
        if path:
            self._load_file(path)

    @logger
    def on_save(self):
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

    @logger
    def on_zoom(self, event):
        self.manager.zoom(event.x, event.y, 2 if event.delta > 0 else 0.5)
        self.update()

    @logger
    def on_iteration_max(self):
        self.manager.iterations = self.view.iteration.max.var.get()

    @logger
    def on_color(self):
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
        if self.locked_update:
            return
        manager = self.manager
        view = self.view
        with self.lock_update():
            view.positioning.real.var.set(manager.real)
            view.positioning.imaginary.var.set(manager.imaginary)
            view.positioning.zoom.var.set(manager.pixel_size)
            view.iteration.max.var.set(manager.iterations)
            view.iteration.sum.var.set(f"{manager.iter_sum} i")
            view.iteration.per_pixel.var.set(f"{manager.iter_pixel:.2f} i/pxl")
            img = manager.first.image()
            self.view.set_image(img)

    @logger
    def on_random_color(self) -> None:
        rgb = [randint(0, 6) + randint(0, 6) + randint(0, 4) for _ in range(3)]
        self.manager.color(*rgb)
        self.update_colors()
        self.update()

    def update_colors(self) -> None:
        with self.lock_update():
            r, g, b = self.manager.rgb
            self.view.red.set(r)
            self.view.green.set(g)
            self.view.blue.set(b)
            self.view.set_image(self.manager.first.image())
            self.view.set_2nd_image(self.manager.second.image())

    @logger
    def on_resize(self, event) -> None:
        self.manager.resize(event.width, event.height)
        self.view.set_2nd_image(self.manager.second.image())
        self.update()

    @logger
    def on_actualization(self):
        self.manager.resize(self.view.width, self.view.height)
        self.update()

    @logger
    def on_reset(self):
        self.manager.reset()
        self.view.set_2nd_image(self.manager.second.image())
        self.update()
