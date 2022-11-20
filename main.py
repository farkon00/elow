import curses

from table import *
from display import *
from formula.expr import *
from formula import lexer, parser

def render(console, text: str):
    console.clear()
    console.refresh()
    print("".join(["\r\n" if char == "\n" else char for char in text]))

def generate_coords_table(size_x: int, size_y: int) -> Table:
    table = Table()
    for y in range(size_y):
        table.cursor = (0, y)
        for x in range(size_x):
            table.add_cell(Cell(CellType.text, f":{x}:{y}"))
    
    table.cursor = (0, 0)

    return table

def main(console):
    if False:
        table = generate_coords_table(20, 20)
    else:
        with open("out.elow", "rb") as f:
            table = Table.from_elow(f.read())

    console.nodelay(True)
    curses.raw()

    display = Display(TableDisplay(table))
    render(console, display.render())

    controls = display.get_controls()
    controls_dict = controls.get_all()
    while True:
        inp = console.getch()
        if inp != curses.ERR:
            if inp in controls_dict:
                requests = controls_dict[inp]()
                if requests:
                    for req in requests:
                        req.accept(console, controls, display, render)
                render(console, display.render())
if __name__ == "__main__":
    curses.wrapper(main)