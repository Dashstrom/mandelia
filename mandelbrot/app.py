import sys
import os
import random

from typing import Any, Callable, Dict
from math import ceil
from PIL import Image
from time import time
from tkinter.messagebox import (askyesnocancel, showerror, showinfo,
                                askokcancel, askyesno)
from tkinter.simpledialog import askstring
from tkinter import (Button, Canvas, Entry, Event, Frame, Label, Menu,
                     PhotoImage, StringVar, Tk, Toplevel, Widget, ttk,
                     filedialog)

from .fractale import Fractale


if getattr(sys, 'frozen', False):
    PATH = os.path.dirname(sys.executable)
else:
    PATH = os.path.dirname(os.path.realpath(__file__))
ICON_PATH = os.path.join(PATH, "logo.ico")
with open(os.path.join(PATH, "info.txt"), "r", encoding="utf8") as file:
    INFO = file.read()


def error_dropper() -> None:
    """Show when try to do something during screenshot series."""
    showerror("Dropper",
              "Vous ne pouvez pas faire une actualisation "
              "car une série de capture en cours")


def error_actualization() -> None:
    """Show when try to do something during actualization."""
    showerror("Actualisaton",
              "Une actialisation est déja en cours")


def ask_actualization() -> bool:
    """Ask if your when actualize."""
    return askokcancel("Actualisation",
                       "Vous allez lancer une opération lente,"
                       "continuer ?")


def timename() -> str:
    """Return timestamp on hex format."""
    return hex(int(time()))[2:].upper()


class App(Tk):
    """Main App."""

    def __init__(self) -> None:
        Tk.__init__(self)
        self.geometry("500x505")
        try:
            self.iconbitmap(ICON_PATH)
        except Exception:
            pass

        self.title("Mandelbrot")
        self.configure(bg='black')
        self.minsize(width=300, height=300)

        self.progressbar = ProgressBarFractale(self)
        self.workspace = Workspace(self)
        self.main_menu = MainMenu(self)

        self.protocol("WM_DELETE_WINDOW", self.closing)
        self.resizable(width=True, height=True)

        self.bind("<Configure>", self.app_resize)
        self.workspace.fractale.update()
        self.mainloop()

    def closing(self) -> None:
        """Called in closure, kill update thread and close."""
        self.workspace.fractale.stop_update()
        self.destroy()
        sys.exit(0)

    def app_resize(self, event: Event) -> None:
        """Called on resize."""
        self.workspace.config(height=event.height)


class ProgressBarFractale(ttk.Progressbar):
    """Bar of rendering progression."""

    def __init__(self, app: App) -> None:
        super().__init__(app, orient="horizontal", length=100)
        self.pack(side="bottom", fill="x", expand=True)
        self.app = app
        self.value = 100

    @property
    def value(self) -> int:
        return self['value']

    @value.setter
    def value(self, value: int) -> None:
        if value != self.value:
            self['value'] = min(100, max(0, value))
            self.app.update_idletasks()


class BaseMenu(Menu):
    def __init__(self, master: Widget, commands=None, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        if commands is not None:
            self.add_commands(commands)

    def add_commands(self, commands: Dict[str, Callable[[], None]]) -> None:
        """Add many commands."""
        for label, command in commands.items():
            self.add_command(label=label, command=command)


class SettingsMenu(BaseMenu):
    """Menu for settings."""

    def __init__(self, main_menu: 'MainMenu') -> None:
        super().__init__(main_menu, tearoff=0, commands={
            "Statistique": self.command_stat,
            "Information": self.command_info,
            "Iteration": self.command_iteration,
            "Palette": self.command_color,
            "Capturer": self.command_capture,
            "Reset": self.command_reset
        })
        self.app = main_menu.app

    def command_stat(self) -> None:
        """Show statistics about fractale."""
        showinfo("Statistique", self.app.workspace.fractale.stat)

    def command_info(self) -> None:
        """Show information about Mandelbrot and software."""
        showinfo("Information", INFO)

    def command_iteration(self) -> None:
        """Ask to change iterations."""
        if self.app.workspace.fractale.dropping():
            return error_dropper()
        new_i = askstring("Iteration",
                          "Veulliez entrer le nouveau nombre "
                          "d'itération inférieur à 100 000")
        if not new_i:
            return
        try:
            new_i = int(new_i)
        except ValueError:
            showerror("Iteration", "Le nombre entré n'est pas valide")
            return
        if 100_000 < new_i:
            showerror("Iteration", "Le nombre entré est trop grand")
            return
        elif 1 > new_i:
            showerror("Iteration", "Le nombre entré est trop petit")
            return
        self.app.workspace.fractale.iteration_max = new_i
        if self.app.workspace.fractale.updating():
            if askokcancel("Actualisation",
                           "Voulez-vous stoper l'actualisation "
                           "en cours pour en faire une nouvelle ?"):
                self.app.workspace.fractale.update()
            else:
                showinfo("Iteration", "Le changement à bien été éffectué")
        elif askokcancel("Actualisation",
                         "Les changement on bien été pris en compte, "
                         "voulez-vous actualisez ?"):
            self.app.workspace.fractale.update()

    def command_capture(self) -> None:
        """Ask to save screenshot."""
        if self.app.workspace.fractale.dropping():
            return error_dropper()
        elif not self.app.workspace.fractale.image:
            showerror("Enregistrement", "Aucune image à enregistrer")
            return
        path = filedialog.asksaveasfilename(title="Enregistrer la capture",
                                            filetypes=[('All Files', '.*')],
                                            initialfile="Sans titre.png")
        if not path:
            return
        try:
            img: Image.Image = self.app.workspace.fractale.image
            img.save(path, quality=95)
            showinfo("Enregistrement", "Enregistrement effectué avec succès")
        except Exception as err:
            showerror("Enregistrement", f"Une erreur est survenue\n{err}")

    def command_color(self):
        """Open new window for choose colors palette."""
        if self.app.workspace.fractale.dropping():
            return error_dropper()
        palette = PaletteWindow(self.app.workspace.fractale)
        palette.mainloop()

    def command_reset(self):
        self.app.workspace.fractale.reset()
        self.app.workspace.fractale.update()


class HistoricMenu(BaseMenu):
    """Menu for historic of actions."""

    def __init__(self, main_menu: 'MainMenu') -> None:
        super().__init__(main_menu, tearoff=0)
        self.logs_count = 0
        self.app = main_menu.app

    def log(self, record: Any):
        """Log actions."""
        self.logs_count += 1
        if self.logs_count > 20:
            self.delete(str(19))
        self.insert_command(
            index=0,
            label=f"Retour à l'actualisation n°{str(self.logs_count)}",
            command=lambda: self.command_log(record))

    def command_log(self, record: Any) -> None:
        if self.app.workspace.fractale.dropping():
            showerror(
                "Dropper",
                "Vous ne pouvez pas modifier revenir en arrière pendant une "
                "série de capture")
        reply = askyesnocancel(
            "Actalisation",
            "Statistique de l'actualisation\n\n"
            f"{self.app.workspace.fractale.stat}\n"
            "Voulez-vous conserver les paramètres actuels ?")
        self.app.workspace.fractale.set(reply, *record)
        self.app.workspace.fractale.update()


class PaletteWindow(Toplevel):
    """Window for change colors."""

    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        self.fractale = app.workspace.fractale
        self.title("Palette")
        self.configure(bg='white')
        self.geometry("300x170")
        self.resizable(width=False, height=False)
        try:
            self.iconbitmap(ICON_PATH)
        except Exception:
            pass
        self.label = Label(
            self, text="Modifiez les valeurs dans les équations ci-dessous")
        self.label.pack()
        self.canvas_palette = Canvas(self, width=256, height=30, bd=0,
                                     highlightthickness=0)
        self.rgb = self.fractale.colors
        self.index_sample = self.canvas_palette.create_image(
            0, 0, image=self.sample, anchor="nw")
        names_colors = ["Rouge", "Vert", "Bleu"]
        self.params = []
        for color, name in zip(self.rgb, names_colors):
            param = StringVar(self, color)
            frame = Frame(self)
            frame.pack()
            label_color_name = Label(frame, text=name, bg="white", width=4)
            label_color_name.pack(side='left')
            parenthesis = Label(frame, text="= (", bg="white")
            parenthesis.pack(side='left')
            entry = Entry(frame, width=7, textvariable=param)
            entry.pack(side='left')
            modulo = Label(frame, text="x itérations) [256]", bg="white")
            modulo.pack(side='left')
            param.trace("w", lambda *args: self.update_colors())
            self.params.append(param)

        self.update_colors()
        self.canvas_palette.pack()
        button_random = Button(self, text="Surprend-moi (⁄ ⁄•⁄ω⁄•⁄ ⁄)",
                               command=self.random_colors, width=26)
        button_random.pack()
        button_end = Button(self, text="Appliquer les changements",
                            command=self.close, width=26)
        button_end.pack()

    def update_colors(self) -> None:
        """Called for every refresh of entry."""
        try:
            rgb = []
            for i, param in enumerate(self.params):
                rgb.append(float(param.get()))
                if not 0 <= rgb[i] < 256:
                    raise ValueError("Mauvais input")
        except ValueError:
            print("Couleur invalide")
        else:
            self.rgb = rgb
            if self.index_sample:
                self.canvas_palette.delete(self.index_sample)
            self.index_sample = self.canvas_palette.create_image(
                0, 0, image=self.sample, anchor="nw")

    def random_colors(self) -> None:
        """Make a random palette."""
        for param in self.params:
            param.set(str(random.randint(0, 6) + random.randint(0, 6)))
        self.update_colors()

    def close(self) -> None:
        """Close palette window."""
        self.destroy()
        self.apply()
        if askyesno("Actualisation",
                    "Voulez-vous lancer une actualisation dès maintenant ?"):
            self.fractale.update()

    def apply(self) -> None:
        """Apply change to fractale."""
        self.fractale.colors = self.rgb

    @property
    def sample(self) -> PhotoImage:
        """Return Tkinter Photo from fractale randering."""
        self.__sample = self.fractale.palette(*self.rgb)
        return self.__sample


class MainMenu(BaseMenu):
    """Main menu at top."""

    def __init__(self, app) -> None:
        super().__init__(app, commands={"Actualiser": self.command_update})
        self.app = app
        self.settings_menu = SettingsMenu(self)
        self.historic_menu = HistoricMenu(self)
        self.add_cascade(label="Option", menu=self.settings_menu)
        self.add_cascade(label="Historique", menu=self.historic_menu)
        self.app.config(menu=self)
        self.historique = 0
        self.rgb = [*self.app.workspace.fractale.colors]

    def command_update(self) -> None:
        """Ask for refresh display."""
        if self.app.workspace.fractale.dropping():
            return error_dropper()
        elif self.app.workspace.fractale.updating():
            return error_actualization()
        elif ask_actualization():
            self.app.workspace.fractale.update()


class Workspace(Canvas):
    """Area for display fractale."""

    def __init__(self, app: App) -> None:
        super().__init__(app, width=500, height=500,
                         bd=0, highlightthickness=0, bg="black")
        self.pack(side="top", fill="both", expand=True)
        self.update()
        self.app = app
        self.fractale = Fractale(self)
        self.selection = False
        self.last_pos_x = self.last_pos_y = 0
        self.__old_w = 500
        self.__old_h = 500
        print()

        self.bind("<Configure>", self.work_resize)
        self.bind("<Button-1>", self.event_click)
        self.bind("<B1-Motion>", self.event_move)
        self.bind("<ButtonRelease-1>", self.event_release)
        self.bind('<Double-Button-1>', self.event_drop)

    @property
    def w(self) -> int:
        return self.winfo_width()

    @property
    def h(self) -> int:
        return self.winfo_height()

    def event_click(self, event: Event) -> None:
        """Start selection."""
        if self.selection:
            self.delete(self.selection)
            self.selection = False
        self.last_pos_x, self.last_pos_y = event.x, event.y

    def event_move(self, event: Event) -> None:
        """Move the selection."""
        if (abs(event.x - self.last_pos_x) / self.w >
                abs(event.y - self.last_pos_y) / self.h):
            select_y = int(abs(event.x - self.last_pos_x) * (self.h / self.w))
            select_x = abs(event.x - self.last_pos_x)
        else:
            select_y = abs(event.y - self.last_pos_y)
            select_x = int(abs(event.y - self.last_pos_y) * (self.w / self.h))
        if (event.x - self.last_pos_x) < 0:
            select_x = -select_x
        if (event.y - self.last_pos_y) < 0:
            select_y = -select_y
        if self.selection:
            self.coords(self.selection, self.last_pos_x, self.last_pos_y,
                        self.last_pos_x + select_x, self.last_pos_y + select_y)
        else:
            self.selection = self.create_rectangle(
                self.last_pos_x, self.last_pos_y,  self.last_pos_x+select_x,
                self.last_pos_y + select_y, outline='red', width=1)

    def event_release(self, event: Event) -> None:
        """End selection."""
        if self.selection:
            pos = self.coords(self.selection)
            self.delete(self.selection)
            self.selection = False
            if self.fractale.dropping():
                showerror(
                    "Dropper",
                    "L'agrandisement est bloqué car une serie de capture")
            elif self.fractale.updating():
                showerror(
                    "Actualisation",
                    "L'agrandisement est bloqué car une "
                    "actualisationest en cours")
            elif askokcancel(
                    "Actualisation",
                    "Attention vous ne pourez plus revenir en arrière "
                    "sans refaire une actualisation"):
                self.fractale.select(*pos)

    def event_drop(self, event: Event) -> None:
        """Double click for make gif."""
        if self.fractale.dropping():
            return error_dropper()
        elif askokcancel("Dropper",
                         "Attention, le rendu d'un gif peu être lent.\n"
                         "Voulez-vous continuez ?"):
            images = self.fractale.drop(event.x, event.y)
            name = hex(int(time()))[2:].upper() + ".gif"
            while True:
                path = filedialog.asksaveasfilename(
                    title="Enregistrer le gif",
                    filetypes=[('Gif Files', '.gif')],
                    initialfile=name)

                if not path:
                    response = askyesno(
                        "Enregistrement",
                        "Etes-vous sur de vouloir quitter abandonner "
                        "enregistrement?")
                    if response:
                        return
                try:
                    print("start saving")
                    images[0].save(path, fromat='GIF', save_all=True,
                                   append_images=images[1:], optimize=True,
                                   duration=10, loop=0, palette=Image.ADAPTIVE,
                                   disposal=2)
                    print("sucess saving")
                    showinfo("Enregistrement",
                             "Enregistrement effectué avec succès")
                    return
                except Exception as err:
                    print("failed to save")
                    retry = askyesno("Enregistrement",
                                     "Une erreur est survenue lors de "
                                     f"l'enregistrement\n{err}\n\n"
                                     "Voulez-vous réssayer ?")
                    if not retry:
                        return

    def progress(self, x: int) -> None:
        self.app.progressbar.value = ceil(x * 100)

    def work_resize(self, event: Event) -> None:
        """Resize fractale with workspace size."""
        f = self.fractale
        f.x2 = f.x1 + (f.x2-f.x1)*(event.width/self.__old_w)
        f.y2 = f.y1 + (f.y2-f.y1)*(event.height/self.__old_h)
        self.__old_w = self.w
        self.__old_h = self.h
