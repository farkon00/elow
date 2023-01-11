import curses
from curses import textpad
from typing import Dict


class Controls:
    def __init__(self, regular: Dict[int, "function"] = None, always_on: Dict[int, "function"] = None):
        self.regular = {} if regular is None else regular
        self.always_on = {} if always_on is None else always_on

    def get_all(self) -> Dict[int, "function"]:
        return self.regular | self.always_on

    def __add__(self, other: "Controls"):
        return Controls(
            self.regular | other.regular,
            self.always_on | other.always_on
        )


class TextBoxRequest:
    def __init__(self, on_finish=None):
        self.on_finish = on_finish if on_finish is not None else lambda _: None

    def _controls_validator(self, char, controls: Dict[int, "function"], console,
                            display: "Display", render: "function") -> int:
        if char == ord("\n"):
            curses.curs_set(0) # Inivisible
            return 7
        elif char in controls:
            ret = controls[char]()
            render(console, display.render())
            if not isinstance(ret, int) and ret is not None:
                assert False, "Unreachable, requests can't process a request"
            if ret is None:
                return 7
            else:
                return ret

        return char

    def accept(self, console, controls: Controls, display: "Display", render: "function"):
        print("\r\n")
        curses.curs_set(1) # Normal
        textbox = textpad.Textbox(console, insert_mode=True)
        self.on_finish(
            textbox.edit(
                lambda char: self._controls_validator(char, controls.always_on, console, display, render),
            ).removesuffix(" \n")
        )