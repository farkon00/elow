import struct

from enum import Enum, auto
from typing import Dict, Iterator

from utils import next_bytes, next_int, next_float

class CellType(Enum):
    none = auto()
    number = auto()
    text = auto()

class Cell:
    def __init__(self, cell_type: CellType = CellType.none, value: object = None):
        self.type = cell_type
        self.value: object = value


    @classmethod
    def parse_none_cell(cls, table: "Table", _):
        table.add_cell(Cell())

    @classmethod
    def parse_text_cell(cls, table: "Table", content: Iterator):
        table.add_cell(Cell(CellType.text,
            next_bytes(content, size=next_int(content)).decode("utf-8")
        ))

    @classmethod
    def parse_number_cell(cls, table: "Table", content: Iterator):
        table.add_cell(Cell(CellType.number,
            next_float(content)
        ))


    def serealize_cell_type(self) -> bytes:
        return self.type.value.to_bytes(1, "little")

    def serealize_none_cell(self) -> bytes:
        return bytes()

    def serealize_text_cell(self) -> bytes:
        str_bytes = bytes(self.value, encoding="utf-8")
        return len(str_bytes).to_bytes(4, "little") + str_bytes 

    def serealize_number_cell(self) -> bytes:
        return struct.pack("f", self.value)


    def display_none_cell(self) -> str:
        return " "

    def display_text_cell(self) -> str:
        return self.value

    def display_number_cell(self) -> str:
        if self.value.is_integer():
            return str(int(self.value))
        else:
            return f"{self.value:.3f}"

    _cell_displayers: Dict[CellType, "function"] = {
        CellType.none   : display_none_cell,
        CellType.number : display_number_cell,
        CellType.text   : display_text_cell,
    }


    def __str__(self) -> str:
        return self._cell_displayers[self.type](self)