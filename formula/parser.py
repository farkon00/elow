from typing import List

from .token import *

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens