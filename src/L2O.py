
import z3
import sympy as sym
import numpy as np
from sympy import lambdify, Array, sympify
from sympy.utilities.autowrap import autowrap

from utils.logic import get_vars, formula_to_BoolRef

def L2O(formula):

    formula=  formula_to_BoolRef(formula)

    decl_f = formula.decl()
    kind_f = decl_f.kind()
    name_f = decl_f.name()
    sort_f = formula.sort()
    num_args = formula.num_args()
    subf = formula.children()[0]
    decl_subf = subf.decl()
    kind_subf = decl_subf.kind()

    children = formula.children()
    if kind_f == z3.Z3_OP_AND:
        if len(children) == 1:
            return L2O(children[0])
        else:
            return sum([L2O(ch) for ch in children])

    elif kind_f == z3.Z3_OP_OR:
        return sym.prod([L2O(ch) for ch in children])

    elif kind_f == z3.Z3_OP_EQ:
        op0 = sympify(children[0].__str__())
        op1 = sympify(children[1].__str__())
        return (op0-op1)**2

    elif kind_f == z3.Z3_OP_LE or kind_f == z3.Z3_OP_LT:
        op0 = sympify(children[0].__str__())
        op1 = sympify(children[1].__str__())
        return sym.Piecewise((0, op0-op1 < 0), ((op0-op1)**2, True))

    elif kind_f == z3.Z3_OP_GE or kind_f == z3.Z3_OP_GT:
        op0 = sympify(children[0].__str__())
        op1 = sympify(children[1].__str__())
        return sym.Piecewise((0, op1-op0 < 0), ((op0-op1)**2, True))

    elif kind_f == z3.Z3_OP_NOT:
        if kind_subf == z3.Z3_OP_EQ:
            children_subf = subf.children()
            op0 = sympify(children_subf[0].__str__())
            op1 = sympify(children_subf[1].__str__())
            return sym.Piecewise((0, (op0-op1)**2 > 0), (1, True))  
        elif kind_subf == z3.Z3_OP_UNINTERPRETED and subf.num_args()==0 :
            raise Exception("Found negation of boolean")
        else:
            raise Exception("negation is supported only for equalities")
    else:
        raise Exception("kind %s of subformula not supported" % decl_f)


def make_lambda(R, variables, args):
    if args.disable_autowrap:
        L = lambdify([variables], R, 'scipy')      # slower
    else:
        try:
            R_subs = R
            R_subs = R_subs.subs(sym.pi, 3.14159265358979323846)
            R_subs = R_subs.subs(sym.sqrt(2), 1.41421356237309504880)
            R_wrapped = autowrap(R_subs, backend="cython", args=variables)    
            L = lambda X: R_wrapped(*X)
        except Exception as e:
            if args.debug:
                print("Exception:", e)
            else:
                print("An exception has occurred (to print the exception text use debug mode).")
            print("\n\nMake lambda of objective function using sympy lambdify (slower than autowrap).")
            L = lambdify([variables], R, 'scipy')  
    return L


def L2O_lambda(args, formula, variables=None):

    formula = formula_to_BoolRef(formula)

    if not variables:
        variables = get_vars(formula)

    R = L2O(formula)

    L = make_lambda(R, variables, args)

    return L
