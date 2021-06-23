from random import randint
from PIL import Image
from datetime import datetime
from contextlib import contextmanager
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.messagebox import showerror, showinfo
from traceback import print_exc

import numpy as np
import cv2

from mandelbrot.model.manager import FractaleManager
from mandelbrot.view.view import View


def log(func):
    def wrapper(*args, **kwargs):
        str_args = ", ".join(f"{arg!r}" for arg in args)
        str_kwargs = ",".join(f"{k}={arg!r}" for k, arg in kwargs.items())
        str_params = ",".join(part for part in (str_args, str_kwargs) if part)
        print(f"[{datetime.now()}] Call {func.__qualname__}({str_params})")
        return func(*args, **kwargs)
    return wrapper


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
            self.view.canvas.bind("<MouseWheel>", self.on_zoom)
            self.view.canvas.bind("<Configure>", self.on_resize)
            self.view.canvas.bind('<Motion>', self.on_motion)
            self.view.canvas.bind('<Double-1>', self.on_swap)
            self.view.red.trace("w", lambda *_: self.on_color())
            self.view.green.trace("w", lambda *_: self.on_color())
            self.view.blue.trace("w", lambda *_: self.on_color())
            self.view.file.save.config(command=self.on_save)
            self.view.file.load.config(command=self.on_load)
            self.view.iteration.max.var.trace(
                "w", lambda *_: self.on_iteration_max())
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

    @log
    def on_swap(self, event):
        self.manager.swap()
        img1, img2 = self.manager.images()
        self.view.set_image(img1)
        self.view.set_2nd_image(img2)
        self.update()

    @log
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
            img: Image.Image = fractale.screenshot(width, height)
            img.save(data["path"], quality=data["compression"])
        elif p.endswith((".gif", ".mp4")):
            # TODO data for all fractale
            data_frac = fractale.data()
            zoom = fractale.get_zoom()
            speed = data["speed"] / 10
            fractale.top()
            fractale.resize(width, height)
            img = fractale.image()

            def iterate_images():
                while fractale.get_zoom() < zoom:
                    print("image")
                    fractale.middle_zoom(1 + (speed - 1) / data["fps"])
                    print("append")
                    yield fractale.image()
                    print(f"end at zoom {fractale.get_zoom()}/{zoom}")

            if p.endswith(".gif"):
                img.save(data["path"], fromat='GIF', save_all=True,
                         append_images=list(iterate_images()),
                         optimize=True, duration=int(1000 / data["fps"]),
                         loop=0, palette=Image.ADAPTIVE, disposal=1)
            else:
                video = cv2.VideoWriter(data["path"], -1, data["fps"],
                                        (width, height))
                video.write(cv2.cvtColor(np.array(img),  # type: ignore
                                         cv2.COLOR_RGB2BGR))
                for frame in iterate_images():
                    video.write(cv2.cvtColor(np.array(frame),  # type: ignore
                                             cv2.COLOR_RGB2BGR))
                video.release()
            fractale.resize(self.view.width, self.view.height)
            fractale.from_data(data_frac)
            print("end export")

    def on_motion(self, event):
        self.manager.motion(event.x, event.y)
        if self.manager.is_mandelbrot_first():
            img = self.manager.second.image()
            self.view.set_2nd_image(img)

    def _load_file(self, path):
        try:
            self.manager.load(path)
            self.update()
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

    @log
    def on_load(self):
        path = askopenfilename(
            title="Charger la configuration",
            filetypes=[('Mandelbrot configuration Files', '.mbc')],
            initialfile="projet.mbc"
        )
        if path:
            self._load_file(path)

    @log
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
                         "Enregistrement réussi")
            except PermissionError:
                print_exc()
            except OSError:
                print_exc()

    @log
    def on_zoom(self, event):
        self.manager.set_zoom(event.x, event.y, 2 if event.delta > 0 else 0.5)
        self.update()

    @log
    def on_iteration_max(self):
        self.manager.iteration_max = self.view.iteration.max.var.get()

    @log
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

    @log
    def update(self):
        if self.locked_update:
            return
        manager = self.manager
        view = self.view
        with self.lock_update():
            view.positioning.real.var.set(manager.real)
            view.positioning.imaginary.var.set(manager.imaginary)
            view.iteration.max.var.set(manager.iteration_max)
            view.positioning.zoom.var.set(manager.get_zoom())
            view.iteration.sum.var.set(
                f"{manager.iter_sum} i")
            self.view.iteration.per_pixel.var.set(
                f"{manager.iter_pixel:.2f} i/pxl")
            self.view.iteration.per_second.var.set(
                f"{manager.iter_second:.0f} i/s")
            img = manager.first.image()
            self.view.set_image(img)

    @log
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

    @log
    def on_resize(self, event) -> None:
        self.manager.resize(event.width, event.height)
        self.view.set_2nd_image(self.manager.second.image())
        self.update()

    @log
    def on_actualization(self):
        self.manager.resize(self.view.width, self.view.height)
        self.update()

    @log
    def on_reset(self):
        self.manager.reset()
        self.view.set_2nd_image(self.manager.second.image())
        self.update()
