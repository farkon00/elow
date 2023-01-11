from typing import List, Optional

from .token import *

class Lexer:
    OPERATIONS = ["+", "-", "*", "/"]
    SPECIAL_SYMBOLS = {
        "," : TokenType.comma,
        ":" : TokenType.colon,
        "(" : TokenType.l_paren,
        ")" : TokenType.r_paren
    }

    def __init__(self, text: str):
        self.text = text
        self.tokens = []
        self.current_tok = ""

    def _is_number(self, tok: str) -> bool:
        try:
            float(tok)
            return True
        except ValueError:
            return False

    def _end_token(self):
        if self.current_tok:
            if self._is_number(self.current_tok):
                self.tokens.append(Token(TokenType.number, self.current_tok))
            else:
                self.tokens.append(Token(TokenType.identifier, self.current_tok))

        self.current_tok = ""

    def _lex_char(self, char: str) -> Optional[Token]:
        if char in self.SPECIAL_SYMBOLS:
            self._end_token()
            return Token(self.SPECIAL_SYMBOLS[char], char)
        elif char in self.OPERATIONS:
            self._end_token()
            return Token(TokenType.operation, char)
        elif char.isspace():
            self._end_token()
        else:
            self.current_tok += char

    def lex(self) -> List[Token]:
        for char in self.text:
            tok = self._lex_char(char)
            if tok is not None:
                self.tokens.append(tok)

        self._end_token()

        return self.tokens