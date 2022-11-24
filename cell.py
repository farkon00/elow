import struct

from enum import Enum, auto
from typing import Dict, Iterator, Optional

from formula.lexer import Lexer
from formula.parser import Parser
from formula.expr import MaybeFloat, ExprErrorType, expr_error_messages
from utils import next_float, next_length_str

class CellType(Enum):
    none = auto()
    number = auto()
    text = auto()
    formula = auto()

class Cell:
    def __init__(self, table: "Table", cell_type: CellType = CellType.none, value: object = None):
        self.table = table
        self.version = -1
        self.type = cell_type
        self.value: object = value
        self._formula_value: Optional[MaybeFloat] = None


    @classmethod
    def parse_none_cell(cls, table: "Table", _):
        table.add_cell()

    @classmethod
    def parse_text_cell(cls, table: "Table", content: Iterator):
        table.add_cell(CellType.text, next_length_str(content))

    @classmethod
    def parse_number_cell(cls, table: "Table", content: Iterator):
        table.add_cell(CellType.number, next_float(content))

    @classmethod
    def parse_formula_cell(cls, table: "Table", content: Iterator):
        table.add_cell(CellType.formula, 
            Parser(Lexer(next_length_str(content)).lex()).parse(is_main=True)
        )


    def serealize_cell_type(self) -> bytes:
        return self.type.value.to_bytes(1, "little")

    def serealize_none_cell(self) -> bytes:
        return bytes()

    def serealize_text_cell(self) -> bytes:
        text_bytes = bytes(self.value, encoding="utf-8")
        return len(text_bytes).to_bytes(4, "little") + text_bytes 

    def serealize_formula_cell(self) -> bytes:
        text_bytes = bytes(self.value.text, encoding="utf-8")
        return len(text_bytes).to_bytes(4, "little") + text_bytes 

    def serealize_number_cell(self) -> bytes:
        return struct.pack("f", self.value)


    def _display_number(self, num: float) -> str:
        if num.is_integer():
            return str(int(num))
        else:
            return f"{num:.3f}"

    def display_none_cell(self) -> str:
        return " "

    def display_text_cell(self) -> str:
        return self.value

    def display_number_cell(self) -> str:
        return self._display_number(self.value)

    def display_text_cell(self) -> str:
        return self.value

    def display_formula_cell(self) -> str:
        val = self.formula_value
        if isinstance(val, ExprErrorType):
            return expr_error_messages[val]
        return self._display_number(val)

    _cell_displayers: Dict[CellType, "function"] = {
        CellType.none    : display_none_cell,
        CellType.number  : display_number_cell,
        CellType.text    : display_text_cell,
        CellType.formula : display_formula_cell,
    }

    @property
    def formula_value(self) -> MaybeFloat:
        if self.type not in (CellType.formula, CellType.number, CellType.none):
            return ExprErrorType.cell_type_error
        if self.type == CellType.none:
            return 0
        if self.type == CellType.number:
            return self.value
        if self.table.version != self.version:
            self._formula_value = self.value.execute(self.table)
            self.version = self.table.version
        return self._formula_value

    def __str__(self) -> str:
        return self._cell_displayers[self.type](self)