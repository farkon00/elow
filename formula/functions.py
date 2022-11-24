import math

from typing import List, Dict, Optional

from .expr import MaybeFloat, MaybeFloatList, Expr, ExprErrorType

def execute_args(table: "Table", args: List[Expr], count: Optional[int] = None) -> MaybeFloatList:
    res = []
    for arg in args:
        res.append(arg.execute(table))
        if isinstance(res[-1], ExprErrorType):
            return res[-1]
    
    if count is not None and count != len(res):
        return ExprErrorType.argument_error
    
    return res
    

def to_elow_function(f: "function", count: Optional[int] = None) -> MaybeFloat:
    def temp(table: "Table", args_expr: List[Expr]):
        args = execute_args(table, args_expr, count=count)
        if isinstance(args, ExprErrorType):
            return args

        return f(args)

    return temp    

def elow_sum(args: List[int]) -> float:
    return sum(args)

def elow_pi(args: List[int]) -> float:
    return math.pi

def elow_abs(args: List[int]) -> float:
    return abs(args[0])

elow_functions: Dict[str, "function"] = {
    k : to_elow_function(v[0], count=v[1]) for k, v in 
    {
        "sum" : (elow_sum, None),
        "pi"  : (elow_pi,  0),
        "abs" : (elow_abs, 1),
    }.items()
}