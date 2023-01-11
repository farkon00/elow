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
    HIGHER_OPERATIONS: List[str] = ["*", "/"]
    LOWER_OPERATIONS: List[str] = ["+", "-"]

    def __init__(self, tokens: List[Token]):
        self.tokens: QueuedIter[Union[Token, Expr]] = QueuedIter(tokens)
        self.new_tokens: List[Union[Token, Expr]] = []

    def _expect(self, token_type: TokenType) -> Token:
        token = self._next_token()
        if token.type != token_type:
            raise InvalidFormula
        return token

    def _next_token(self) -> Token | Expr:
        try:
            return next(self.tokens)
        except StopIteration:
            raise InvalidFormula
    
    def _parse_number(self, token: Token):
        self.new_tokens.append(Expr(token.value, ExprType.constant, value=float(token.value)))

    def _parse_cell(self, token: Token):
        col = self._expect(TokenType.number)
        self._expect(TokenType.colon)
        row = self._expect(TokenType.number)
        
        x, y = float(col.value), float(row.value)
        if not x.is_integer() or not y.is_integer():
            raise InvalidFormula
        
        self.new_tokens.append(Expr(f":{col.value}:{row.value}", ExprType.cell, value=(int(x), int(y))))

    def _parse_operation(self, token: Token):
        try:
            left = self.new_tokens[-1]
            self.new_tokens = self.new_tokens[:-1]
        except IndexError:
            raise InvalidFormula
        right = self._next_token()
        if not (isinstance(left, Expr) and isinstance(right, Expr)):
            raise InvalidFormula
        self.new_tokens.append(Expr(
            left.text + token.value + right.text,
            self.OPERATIONS[token.value], [left, right]
        ))

    def _parse_function(self, token: Token):
        self._expect(TokenType.l_paren)
        args = []
        first_arg = self._next_token() 
        has_args = first_arg.type != TokenType.r_paren
        if has_args:
            self.tokens.add(first_arg)
        if has_args:
            while True:
                [arg, *rest] = Parser(list(self.tokens)).parse(end=[TokenType.comma, TokenType.r_paren])
                self.tokens.__init__(rest)
                args.append(arg)
                if self._next_token().type == TokenType.r_paren:
                    break
        self.new_tokens.append(Expr(
            f"{token.value}({', '.join([arg.text for arg in args])})",
            ExprType.func, args, token.value
        ))

    def _parse_parens(self, token: Token):
        [expr, *rest] = Parser(list(self.tokens)).parse(end=[TokenType.r_paren])
        self.tokens.__init__(rest[1:])
        expr.text = f"({expr.text})"
        self.new_tokens.append(expr)

    def _parse_higher_operation(self, token: Token):
        if token.value in self.HIGHER_OPERATIONS:
            self._parse_operation(token)
        else:
            self.new_tokens.append(token)

    def _parse_lower_operation(self, token: Token):
        if token.value in self.LOWER_OPERATIONS:
            self._parse_operation(token)
        else:
            self.new_tokens.append(token)

    ITERATIONS: List[Dict[TokenType, "function"]] = [
        {
            TokenType.identifier : _parse_function,
            TokenType.colon : _parse_cell, 
            TokenType.number : _parse_number,
            TokenType.l_paren : _parse_parens,
        },
        {TokenType.operation : _parse_higher_operation},
        {TokenType.operation : _parse_lower_operation},
    ]

    def parse(self, is_main: bool = False, end: List[str] = []) -> Expr:
        first = self._next_token()
        if first.type in end:
            raise InvalidFormula
        self.tokens.add(first)

        for it, iteration in enumerate(self.ITERATIONS):
            for token in self.tokens:
                if isinstance(token, Expr):
                    self.new_tokens.append(token)
                    continue
                if token.type in end:
                    self.new_tokens.extend([token, *self.tokens])
                    break

                if token.type not in iteration:
                    self.new_tokens.append(token)
                else:
                    iteration[token.type](self, token)
            else:
                if end:
                    raise InvalidFormula
            self.tokens = QueuedIter(self.new_tokens.copy())
            self.new_tokens = []


        if is_main:
            final_tokens = list(self.tokens)

            if len(final_tokens) != 1:
                raise InvalidFormula

            return final_tokens[0]
        else:
            return list(self.tokens)