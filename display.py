from typing import List, Tuple

from table import Table, Cell

class TableDisplay:
    def __init__(self, table: Table):
        self.table = table
        self.window_size: Tuple[int, int] = (12, 12)
        self.window_pos: Tuple[int, int] = (0, 0)

    def _get_window(self) -> List[List[Cell]]:
        return self.table.rows[self.window_pos[1]:self.window_pos[1]+self.window_size[1]]

    def _get_col_sizes(self) -> List[int]:
        col_sizes = [1 for _ in range(self.window_size[1])]
        for row in self._get_window():
            for col, cell in enumerate(row[self.window_pos[0]:self.window_pos[0]+self.window_size[0]]):
                col_sizes[col] = max(len(str(cell)), col_sizes[col])

        return col_sizes

    def render(self) -> str:
        col_sizes = self._get_col_sizes()
        string_table: List[List[str]] = []
        for row in self._get_window():
            string_row = []
            for cell, col_size in zip(row, col_sizes):
                string_cell = str(cell)
                string_row.append(string_cell + (col_size-len(string_cell)) * " ")
            string_table.append(string_row)
        return "\n".join([" ".join(row) for row in string_table])

class Display:
    def __init__(self, table_display: TableDisplay):
        self.table_display = table_display

    def render(self) -> str:
        return self.table_display.render()