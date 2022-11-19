import curses

from table import *
from display import *

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
        table = Table()
        table.add_cell(Cell(CellType.text, "Hi"))
        table.add_cell(Cell(CellType.none))
        table.add_cell(Cell(CellType.text, "Bye"))
        table.cursor = (0, 1)

        table.add_cell(Cell(CellType.number, 12345.0))
        table.add_cell(Cell(CellType.number, 1.1))
        table.add_cell(Cell(CellType.number, 1.0))
        table.add_cell(Cell(CellType.number, 69.0))

        with open("test.elow", "wb") as f:
            f.write(table.to_elow())
    else:
        # with open("test.elow", "rb") as f:
        #     table = Table.from_elow(f.read())
        table = generate_coords_table(20, 20)

    console.nodelay(True)

    display = Display(TableDisplay(table))
    render(console, display.render())

    controls = display.get_controls()
    while True:
        inp = console.getch()
        if inp != curses.ERR:
            if inp in controls:
                controls[inp]()
                render(console, display.render())
            else:
                print(inp)

if __name__ == "__main__":
    curses.wrapper(main)