from abc import ABC
import tkinter as tk
from tkinter.constants import LEFT, NW, HORIZONTAL, FALSE, X, SUNKEN
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T", tk.StringVar, tk.IntVar, tk.DoubleVar, tk.BooleanVar)


class Labeled(tk.Frame, ABC):
    """Label for another widget."""
    def __init__(self, master: Optional[tk.Misc], text: str) -> None:
        """Instantiate Labeled."""
        super().__init__(master)
        self.label = tk.Label(self, text=text, width=10, anchor=NW)
        self.label.pack(side=LEFT)


class VariableContainer(Generic[T]):
    """Contain a variable."""
    def __init__(self, var: T) -> None:
        """Instantiate Labeled."""
        self.__var: T = var

    @property
    def var(self) -> T:
        """Get the variable."""
        return self.__var


class AdjustableInput(Labeled, VariableContainer[tk.DoubleVar]):
    """Widget to have a variable with a scale and an entry."""
    def __init__(self, master: Optional[tk.Misc], text: str, min_: int,
                 default: int, max_: int, entry_width: int = 6) -> None:
        """Instantiate AdjustableInput."""
        Labeled.__init__(self, master, text)
        VariableContainer.__init__(self, tk.DoubleVar(self, float(default)))
        self.min = min_
        self.max = max_
        self.default = default
        self.__error = False
        self.entry_var = tk.StringVar(self, str(self.default))
        self.scale = tk.Scale(self, from_=self.min, to=self.max,
                              sliderlength=30, orient=HORIZONTAL,
                              variable=self.var, showvalue=FALSE)
        self.entry = tk.Entry(self, width=entry_width,
                              textvariable=self.entry_var)
        self.scale.pack(side=LEFT, fill=X, expand=True)
        self.entry.pack(side=LEFT, padx=3)
        self.entry_var.trace("w", self.on_update_scale)
        self.var.trace("w", self.on_update_entry)
        self.entry.bind("<FocusOut>", self._event_focus_out)
        self.entry.bind("<KeyPress>", self.on_keypress)

    def on_keypress(self, event) -> None:
        """Handle keypress"""
        delta = {"Down": -1, "Up": 1}.get(event.keysym, 0)
        if delta:
            self.var.set(max(self.var.get() + delta, self.min))

    def disable(self) -> None:
        """Disable the entry."""
        self.entry["state"] = "disable"
        self.scale["sliderrelief"] = "sunken"
        self.scale["state"] = "disable"
        self.label["state"] = "disable"

    def enable(self) -> None:
        """Enable the entry."""
        self.entry["state"] = "normal"
        self.scale["sliderrelief"] = "raised"
        self.scale["state"] = "normal"
        self.label["state"] = "normal"

    @property
    def error(self) -> bool:
        """Get the error state."""
        return self.__error

    @error.setter
    def error(self, state: Any) -> None:
        """Set error on true or false."""
        self.__error = bool(state)
        self.entry.configure(bg="red" if self.__error else "white")

    def on_update_scale(self, *_: Any) -> None:
        """Called for update the scale."""
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

    def on_update_entry(self, *_: Any) -> None:
        """Called for update the entry."""
        self.entry_var.set(str(int(self.var.get())))

    def _event_focus_out(self, *_: Any) -> None:
        """Return to the previous valid state."""
        if self.error:
            try:
                int(self.entry_var.get())
            except ValueError:
                min_chars = max(len(str(self.min)), 1)
                nb_chars = len(self.entry_var.get())
                if nb_chars < min_chars:
                    self.scale.set(str(self.min))
            self.on_update_entry(self)


class Output(Labeled, VariableContainer[tk.StringVar]):
    """Read-Only Entry."""
    def __init__(self, master: Optional[tk.Misc],
                 text: str, default: Any) -> None:
        """Instantiate Output."""
        Labeled.__init__(self, master, text)
        VariableContainer.__init__(self, tk.StringVar(self, str(default)))
        self.sep = tk.Label(self, text=":")
        self.output_label = tk.Label(self, relief=SUNKEN, anchor=NW,
                                     textvariable=self.var, width=25)
        self.sep.pack(side=LEFT)
        self.output_label.pack(side=LEFT, fill=X, expand=True, padx=2, pady=2)


class InputOutput(Labeled, VariableContainer[tk.StringVar]):
    """Writable Entry."""
    def __init__(self, master: Optional[tk.Misc], text, default: Any) -> None:
        """Instantiate InputOutput."""
        Labeled.__init__(self, master, text)
        VariableContainer.__init__(self, tk.StringVar(self, str(default)))
        self.sep = tk.Label(self, text=":")
        self.entry = tk.Entry(self, textvariable=self.var, width=32)
        self.sep.pack(side=LEFT)
        self.entry.pack(side=LEFT, fill=X, padx=3)
