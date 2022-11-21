from typing import List, Dict

from .expr import MaybeFloat, MaybeFloatList, Expr, ExprErrorType

def execute_args(table: "Table", args: List[Expr], count=None) -> MaybeFloatList:
    res = []
    for arg in args:
        res.append(arg.execute(table))
        if isinstance(res[-1], ExprErrorType):
            return res[-1]
    
    if count is not None and count != len(res):
        return ExprErrorType.argument_error
    
    return res
    

def elow_sum(table: "Table", args_expr: List[Expr]) -> MaybeFloat:
    args = execute_args(table, args_expr)
    if isinstance(args, ExprErrorType):
        return args
    
    return sum(args)

elow_functions: Dict[str, "function"] = {
    "sum" : elow_sum
}