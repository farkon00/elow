from typing import List

from .token import *
from .expr import *
from utils import QueuedIter

class InvalidFormula(BaseException):
    pass

class Parser:
    OPERATIONS: Dict[str, ExprType] = {
        "+" : ExprType.add,
        "-" : ExprType.sub,
        "*" : ExprType.mul,
        "/" : ExprType.div,
    }

    def __init__(self, tokens: List[Token]):
        self.tokens = QueuedIter(tokens)
        self._last_expr = None

    @property
    def last_expr(self):
        return self._last_expr

    @last_expr.setter
    def last_expr(self, val):
        if val is not None and self._last_expr is not None:
            raise InvalidFormula    
        self._last_expr = val

    def _expect(self, token_type: TokenType) -> Token:
        token = next(self.tokens)
        if token.type != token_type:
            raise InvalidFormula
        return token

    def parse(self, end: List[str] = []) -> Expr:
        first = next(self.tokens)
        if first.type in end:
            raise InvalidFormula()
        self.tokens.add(first)

        for token in self.tokens:
            if token.type in end:
                self.tokens.add(token)
                break
                
            if token.type == TokenType.number:
                self.last_expr = Expr(token.value, ExprType.constant, value=float(token.value))
            elif token.type == TokenType.colon:
                col = self._expect(TokenType.number)
                self._expect(TokenType.colon)
                row = self._expect(TokenType.number)
                
                x, y = float(col.value), float(row.value)
                if not x.is_integer() or not y.is_integer():
                    raise InvalidFormula
                
                self.last_expr = Expr(f":{col.value}:{row.value}", ExprType.cell, value=(int(x), int(y)))
            elif token.type == TokenType.operation:
                if self.last_expr is None:
                    raise InvalidFormula
                
                left = self.last_expr
                self.last_expr = None
                right = self.parse(end=end)
                self.last_expr = None
                self.last_expr = Expr(
                    left.text + token.value + right.text,
                    self.OPERATIONS[token.value], [left, right]
                )
            elif token.type == TokenType.identifier: # function
                self._expect(TokenType.l_paren)
                args = []
                first_arg = next(self.tokens) 
                has_args = first_arg.type != TokenType.r_paren
                if has_args:
                    self.tokens.add(first_arg)
                if has_args:
                    while True:
                        self.last_expr = None
                        arg = self.parse(end=[TokenType.comma, TokenType.r_paren])
                        args.append(arg)
                        if next(self.tokens).type == TokenType.r_paren:
                            break
                self.last_expr = None
                self.last_expr = Expr(
                    f"{token.value}({', '.join([arg.text for arg in args])})",
                    ExprType.func, args, token.value
                )
            else:
                raise InvalidFormula
        else:
            if end:
                raise InvalidFormula

        return self.last_expr
