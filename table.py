from typing import List, Dict, Tuple

from cell import Cell, CellType
from utils import next_bytes

MAGIC = bytes([0xE]) + bytes("LOW", encoding="utf-8")

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
            res = res + bytes([0])
        return res

    def save_to(self, file_name: str):
        with open(file_name, "wb") as f:
            f.write(self.to_elow())

    @classmethod
    def from_elow(cls, file_content: bytes) -> "Table":
        table = Table()
        content = iter(file_content)

        if next_bytes(content, len(MAGIC)) != MAGIC:
            print("Invalid file")
            exit(1) # TODO: Make actually good erros

        for cell_type in content:
            if cell_type == 0: # New line
                table.cursor = (table.cursor[0], table.cursor[1]+1)
            else:
                cls._cell_parsers[cell_type](table, content)

        table.cursor = (0, 0)

        return table