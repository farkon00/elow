from typing import Dict

from request import TextBoxRequest

class Pallet:
    def __init__(self, table_display: "TableDisplay"):
        self.table_display = table_display

    def get_request(self) -> TextBoxRequest:
        return TextBoxRequest(on_finish = lambda text: self._on_finish(text))

    def _save_command(self):
        self.table_display.table.save_to("out.elow")

    def _exit_command(self):
        exit()

    COMMANDS: Dict[str, "function"] = {
        "save" : _save_command,
        "exit" : _exit_command,
    }

    def _on_finish(self, text: str):
        if text.strip() in self.COMMANDS:
            self.COMMANDS[text.strip()](self)