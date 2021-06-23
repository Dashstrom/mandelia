from abc import ABC
from tkinter import *
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T", StringVar, IntVar, DoubleVar, BooleanVar)


class Labeled(Frame, ABC):
    def __init__(self, master: Optional[Misc], text: str) -> None:
        super().__init__(master)
        self.label = Label(self, text=text, width=10, anchor=NW)
        self.label.pack(side=LEFT)


class VariableContainer(Generic[T]):
    def __init__(self, var: T) -> None:
        self.__var: T = var

    @property
    def var(self) -> T:
        return self.__var


class AdjustableInput(Labeled, VariableContainer[DoubleVar]):

    def __init__(self, master: Optional[Misc], text: str, min_: int,
                 default: int, max_: int, entry_width: int = 6) -> None:
        Labeled.__init__(self, master, text)
        VariableContainer.__init__(self, DoubleVar(self, float(default)))
        self.min = min_
        self.max = max_
        self.default = default
        self.__error = False
        self.entry_var = StringVar(self, str(self.default))
        self.scale = Scale(self, from_=self.min, to=self.max, sliderlength=30,
                           orient=HORIZONTAL, variable=self.var,
                           showvalue=FALSE)
        self.entry = Entry(self, width=entry_width,
                           textvariable=self.entry_var)
        self.scale.pack(side=LEFT, fill=X, expand=True)
        self.entry.pack(side=LEFT, padx=3)
        self.entry_var.trace("w", self._update_scale)
        self.var.trace("w", self._update_entry)
        self.entry.bind("<FocusOut>", self._event_focus_out)
        self.entry.bind("<KeyPress>", self.on_keypress)

    def on_keypress(self, event) -> None:
        if event.keysym == "Down":
            self.var.set(max(self.var.get() - 1, self.min))
        elif event.keysym == "Up":
            self.var.set(min(self.var.get() + 1, self.max))

    def disable(self) -> None:
        self.entry["state"] = "disable"
        self.scale["sliderrelief"] = "sunken"
        self.scale["state"] = "disable"
        self.label["state"] = "disable"

    def enable(self) -> None:
        self.entry["state"] = "normal"
        self.scale["sliderrelief"] = "raised"
        self.scale["state"] = "normal"
        self.label["state"] = "normal"

    @property
    def error(self) -> bool:
        return self.__error

    @error.setter
    def error(self, state: Any) -> None:
        self.__error = bool(state)
        self.entry.configure(bg="red" if self.__error else "white")

    def _update_scale(self, *_: Any) -> None:
        text = self.entry_var.get()
        self.error = False
        max_chars = max(len(str(self.max)), 1)
        nb_chars = len(self.entry_var.get())
        if nb_chars > max_chars:
            text = text[:max_chars]
            self.entry_var.set(text)

        try:
            value = int(text)
        except ValueError:
            self.error = True
        else:
            if self.min > value:
                self.error = True
            elif self.max < value:
                self.entry_var.set(str(self.max))
                self.scale.set(self.max)
            else:
                self.scale.set(value)

    def _update_entry(self, *_: Any) -> None:
        self.entry_var.set(str(int(self.var.get())))

    def _event_focus_out(self, *_: Any) -> None:
        if self.error:
            try:
                int(self.entry_var.get())
            except ValueError:
                min_chars = max(len(str(self.min)), 1)
                nb_chars = len(self.entry_var.get())
                if nb_chars < min_chars:
                    self.scale.set(str(self.min))
            self._update_entry(self)


class Output(Labeled, VariableContainer[StringVar]):
    def __init__(self, master: Optional[Misc],
                 text: str, default: Any) -> None:
        Labeled.__init__(self, master, text)
        VariableContainer.__init__(self, StringVar(self, str(default)))
        self.sep = Label(self, text=":")
        self.output_label = Label(self, relief=SUNKEN, anchor=NW,
                                  textvariable=self.var)
        self.sep.pack(side=LEFT)
        self.output_label.pack(side=LEFT, fill=X, expand=True, padx=2, pady=2)


class InputOutput(Labeled, VariableContainer[StringVar]):
    def __init__(self, master: Optional[Misc], text, default: Any) -> None:
        Labeled.__init__(self, master, text)
        VariableContainer.__init__(self, StringVar(self, str(default)))
        self.sep = Label(self, text=":")
        self.entry = Entry(self, textvariable=self.var, width=32)
        self.sep.pack(side=LEFT)
        self.entry.pack(side=LEFT, fill=X, padx=3)
