from enum import Enum, auto
from typing import List, Dict, Optional

from cell import CellType 

class ExprType(Enum):
    cell = auto()
    constant = auto()
    func = auto()

    add = auto()
    sub = auto()
    mul = auto()
    div = auto()

class ExprErrorType(Enum):
    cell_type_error = auto() 

MaybeFloat = float | ExprErrorType


class Expr:
    def __init__(self, type: ExprType, arguments: List["Expr"] = None, value: Optional[object] = None):
        self.type = type
        self.arguments = [] if arguments is None else arguments
        self.value = value

    def _execute_cell_expr(self, table: "Table") -> MaybeFloat:
        cell = table.rows[self.value[1]][self.value[0]]
        if cell.type != CellType.number:
            return ExprErrorType.cell_type_error
        return cell.value

    def _execute_constant_expr(self, table: "Table") -> float:
        return self.value

    def _execute_func_expr(self, table: "Table") -> MaybeFloat:
        assert False, "Not implemented"

    def _error_execute(self, a: MaybeFloat, b: MaybeFloat, f: "function") -> MaybeFloat:
        if isinstance(a, ExprErrorType):
            return a
        if isinstance(b, ExprErrorType):
            return b
        
        return f(a, b)

    def _execute_binary_expr(self, table: "Table", f: "function") -> MaybeFloat:
        return self._error_execute(
            self.arguments[0].execute(table), self.arguments[1].execute(table),
            f
        )

    def _execute_add_expr(self, table: "Table") -> MaybeFloat:
        return self._execute_binary_expr(table, lambda a, b: a + b)

    def _execute_sub_expr(self, table: "Table") -> MaybeFloat:
        return self._execute_binary_expr(table, lambda a, b: a - b)

    def _execute_mul_expr(self, table: "Table") -> MaybeFloat:
        return self._execute_binary_expr(table, lambda a, b: a * b)

    def _execute_div_expr(self, table: "Table") -> MaybeFloat:
        return self._execute_binary_expr(table, lambda a, b: a / b)

    _expr_type_executors: Dict[ExprType, "function"] = {
        ExprType.cell     : _execute_cell_expr,
        ExprType.constant : _execute_constant_expr,
        ExprType.func     : _execute_func_expr,

        ExprType.add : _execute_add_expr,
        ExprType.sub : _execute_sub_expr,
        ExprType.mul : _execute_mul_expr,
        ExprType.div : _execute_div_expr,
    }

    def execute(self, table: "Table") -> MaybeFloat:
        return self._expr_type_executors[self.type](self, table)