import curses # Key constants

from typing import List, Tuple

from table import Table, Cell, CellType
from request import TextBoxRequest, Controls

class TableDisplay:
    def __init__(self, table: Table):
        self.table = table
        self.window_size: Tuple[int, int] = (12, 12)
        self.window_pos: Tuple[int, int] = (0, 0)

    def to_win_x(self, x: int):
        return x - self.window_pos[0]

    def to_win_y(self, y: int):
        return y - self.window_pos[1]

    def to_win_coords(self, coords: Tuple[int, int]):
        return (self.to_win_x(coords[0]), self.to_win_y(coords[1]))

    def _get_window(self) -> List[List[Cell]]:
        return [row[self.window_pos[0]:self.window_pos[0]+self.window_size[0]] for row in 
            self.table.rows[self.window_pos[1]:self.window_pos[1]+self.window_size[1]]]

    def _get_col_sizes(self) -> List[int]:
        col_sizes = [1 for _ in range(self.window_size[1])]
        for row in self._get_window():
            for col, cell in enumerate(row):
                col_sizes[col] = max(len(str(cell)), col_sizes[col])

        return col_sizes

    def _apply_selection_styles(self, text: str) -> str:
        if text.isspace():
            return "\033[47m" + text + "\033[0m"
        else:
            return "\033[1m" + text + "\033[0m"

    def update_win_pos_by_cursor(self):
        cursor = self.to_win_coords(self.table.cursor)
        if cursor[0] >= self.window_size[0]:
            self.window_pos = (self.table.cursor[0]-self.window_size[0]+1, self.window_pos[1])
        if cursor[1] >= self.window_size[1]:
            self.window_pos = (self.window_pos[0], self.table.cursor[1]-self.window_size[1]+1)
        if cursor[0] < 0:
            self.window_pos = (self.table.cursor[0], self.window_pos[1])
        if cursor[1] < 0:
            self.window_pos = (self.window_pos[0], self.table.cursor[1])

    def _update_selected_cell(self, text: str):
        if not text:
            self.table.rows[self.table.cursor[1]][self.table.cursor[0]] = \
                Cell(CellType.none)
            return
        try:
            self.table.rows[self.table.cursor[1]][self.table.cursor[0]] = \
                Cell(CellType.number, float(text))
        except ValueError:
            self.table.rows[self.table.cursor[1]][self.table.cursor[0]] = \
                Cell(CellType.text, text)

    def _change_selected_content(self):
        return [TextBoxRequest(self._update_selected_cell)]

    def get_controls(self) -> Controls:
        return Controls(
            regular={
                curses.KEY_UP    : lambda: self.table.move_cursor( 0, -1),
                curses.KEY_DOWN  : lambda: self.table.move_cursor( 0,  1),
                curses.KEY_LEFT  : lambda: self.table.move_cursor(-1,  0),
                curses.KEY_RIGHT : lambda: self.table.move_cursor( 1,  0),
                ord(" ") : self._change_selected_content,
            },
            always_on={
                19 : lambda: self.table.save_to("out.elow") # ctrl + S
            }
        )

    def render(self) -> str:
        self.update_win_pos_by_cursor()
        col_sizes = self._get_col_sizes()
        string_table: List[List[str]] = []
        cursor = self.to_win_coords(self.table.cursor)
        for row in self._get_window():
            string_row = []
            for cell, col_size in zip(row, col_sizes):
                string_cell = str(cell)
                string_row.append(string_cell + (col_size-len(string_cell)) * " ")
            string_table.append(string_row)

        # Make selected cell bold
        string_table[cursor[1]][cursor[0]] = self._apply_selection_styles(string_table[cursor[1]][cursor[0]])

        return "\n".join([" ".join(row) for row in string_table])

# This class is pretty much usless wrapper for now, but it will be used later
class Display:
    def __init__(self, table_display: TableDisplay):
        self.table_display = table_display

    def get_controls(self) -> Controls:
        return Controls(always_on={
            27 : exit, # escape
        }) + self.table_display.get_controls()

    def render(self) -> str:
        return self.table_display.render()