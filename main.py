from table import *
from display import *

def main():
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
        with open("test.elow", "rb") as f:
            table = Table.from_elow(f.read())

    display = Display(TableDisplay(table))
    print(display.render())

if __name__ == "__main__":
    main()