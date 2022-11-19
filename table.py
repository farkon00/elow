import struct

from enum import Enum, auto 
from typing import List, Dict, Tuple, Iterator

from utils import next_bytes, next_int, next_float

MAGIC = bytes([0xE]) + bytes("LOW", encoding="utf-8")

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

class Table:
    _cell_parsers: Dict[CellType, "function"] = {
        CellType.none  .value : Cell.parse_none_cell,
        CellType.number.value : Cell.parse_number_cell,
        CellType.text  .value : Cell.parse_text_cell,
    }

    _cell_serializers: Dict[CellType, "function"] = {
        CellType.none   : Cell.serealize_none_cell,
        CellType.number : Cell.serealize_number_cell,
        CellType.text   : Cell.serealize_text_cell,
    }

    def __init__(self):
        self.rows: List[List[Cell]] = []
        self.cursor: Tuple[int, int] = (0, 0)

    def add_cell(self, cell: Cell):
        if len(self.rows) <= self.cursor[1]:
            self.rows.extend([[] for _ in range(len(self.rows)-self.cursor[1]+1)]) 
        self.rows[self.cursor[1]].insert(self.cursor[0]+1, cell)  
        self.cursor = (self.cursor[0]+1, self.cursor[1])

    def move_cursor(self, dx: int, dy: int):
        self.cursor = (self.cursor[0]+dx, self.cursor[1]+dy)
        
        if self.cursor[0] < 0: 
            self.cursor = (0, self.cursor[1])
        if self.cursor[1] < 0: 
            self.cursor = (self.cursor[0], 0)
        
        if self.cursor[1] >= len(self.rows):
            self.rows.extend(
                [[Cell() for _ in range(self.cursor[0])]
                    for _ in range(self.cursor[1] - len(self.rows) + 1)])

        if self.cursor[0] >= len(self.rows[self.cursor[1]]):
            self.rows[self.cursor[1]].extend(
                [Cell() for _ in 
                    range(self.cursor[0] - len(self.rows[self.cursor[1]]) + 1)]
            )

    def to_elow(self) -> bytes:
        res = MAGIC
        for row in self.rows:
            for cell in row:
                res = res + cell.serealize_cell_type() + self._cell_serializers[cell.type](cell)
            res = res + bytes([255])
        return res

    @classmethod
    def from_elow(cls, file_content: bytes) -> "Table":
        table = Table()
        content = iter(file_content)

        if next_bytes(content, len(MAGIC)) != MAGIC:
            print("Invalid file")
            exit(1) # TODO: Make actually good erros

        for cell_type in content:
            if cell_type == 255:
                table.cursor = (table.cursor[0], table.cursor[1]+1)
            else:
                cls._cell_parsers[cell_type](table, content)

        table.cursor = (0, 0)

        return table