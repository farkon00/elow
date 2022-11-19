from curses import textpad

class TextBoxRequest:
    def __init__(self, on_finish=None):
        self.on_finish = on_finish if on_finish is not None else lambda _: None

    def accept(self, console):
        print("\r\n")
        textbox = textpad.Textbox(console, insert_mode=True)
        self.on_finish(textbox.edit(lambda key: 7 if key == ord("\n") else key).removesuffix("\n"))