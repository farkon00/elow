from dataclasses import dataclass
from enum import Enum, auto

class TokenType(Enum):
    identifier = auto()
    number = auto()
    operation = auto()
    comma = auto()
    colon = auto()
    l_paren = auto()
    r_paren = auto()

@dataclass
class Token:
    type: TokenType
    value: str