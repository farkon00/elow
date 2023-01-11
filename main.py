import sys
import os
import argparse
import curses

from table import *
from display import *
from formula.expr import *
from formula.lexer import Lexer

def render(console, text: str):
    console.clear()
    console.refresh()
    print("".join(["\r\n" if char == "\n" else char for char in text]))

# Debugging tools
def generate_coords_table(size_x: int, size_y: int) -> Table:
    table = Table()
    for y in range(size_y):
        table.cursor = (0, y)
        for x in range(size_x):
            table.add_cell(CellType.text, f":{x}:{y}")
    
    table.cursor = (0, 0)

    return table

def generate_lexer_test_table(text: str) -> Table:
    lexer = Lexer(text)
    tokens = lexer.lex()
    table = Table()
    for row, token in enumerate(tokens):
        table.cursor = (0, row)
        table.add_cell(CellType.text, token.type.name)
        table.add_cell(CellType.text, token.value)
    table.cursor = (0, 0)
    table.save_to("tokens.elow")
    return table

def expr_to_str(expr):
    res = ""
    if isinstance(expr.arguments, list):
        for arg in expr.arguments:
            res += expr_to_str(arg) + "\n"
    return expr.type.name + " " + (str(expr.value) if expr.value is not None else "") +\
        "\n  " + "\n  ".join(res.split("\n"))
# END Debugging tools


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="*.elow file to open in elow editor")
    parser.add_argument("-c", "--create", action="store_true", default=False, dest="create")
    return parser.parse_args(sys.argv[1:])

def load_table() -> Table:
    args = parse_args()
    
    if args.create and not os.path.exists(args.file):
        temp_table = Table()
        temp_table.add_cell()
        temp_table.save_to(args.file)

    with open(args.file, "rb") as f:
        return Table.from_elow(f.read(), args.file)

def main(console, table):
    console.nodelay(True)
    curses.raw()
    curses.curs_set(0) # Inivisible

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
    table = load_table()
    curses.wrapper(lambda console: main(console, table))