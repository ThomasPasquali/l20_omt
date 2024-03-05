
import z3
import re
import sympy as sym
from sympy import lambdify, Array, sympify, latex
from sympy.utilities.autowrap import autowrap

from utils.logic import get_vars_sym, formula_to_BoolRef

def z3BoolRef_to_LaTex(formula, var_names):
    formula = formula_to_BoolRef(formula)

    decl_f = formula.decl()
    kind_f = decl_f.kind()
    subf = formula.children()[0]
    decl_subf = subf.decl()
    kind_subf = decl_subf.kind()

    children = formula.children()
    if kind_f == z3.Z3_OP_AND:
        if len(children) == 1:
            return latex(z3BoolRef_to_LaTex(children[0], var_names))
        else:
            return ' \wedge '.join([f'({z3BoolRef_to_LaTex(ch, var_names)})' for ch in children])

    elif kind_f == z3.Z3_OP_OR:
        return ' \vee '.join([f'({z3BoolRef_to_LaTex(ch, var_names)})' for ch in children])

    elif kind_f == z3.Z3_OP_EQ or kind_f == z3.Z3_OP_LE or kind_f == z3.Z3_OP_LT or kind_f == z3.Z3_OP_GE or kind_f == z3.Z3_OP_GT:
        return latex(sympify(formula.__str__()).subs(var_names))

    elif kind_f == z3.Z3_OP_NOT:
        if kind_subf == z3.Z3_OP_EQ:
            # FIXME
            return latex(sympify(formula.__str__()).subs(var_names))
        elif kind_subf == z3.Z3_OP_UNINTERPRETED and subf.num_args()==0 :
            raise Exception("Found negation of boolean")
        else:
            raise Exception("negation is supported only for equalities")
    else:
        raise Exception("kind %s of subformula not supported" % decl_f)

# TODO double check all cases
def z3BoolRef_to_SymPy(formula):
    formula = formula_to_BoolRef(formula)

    decl_f = formula.decl()
    kind_f = decl_f.kind()
    subf = formula.children()[0]
    decl_subf = subf.decl()
    kind_subf = decl_subf.kind()

    children = formula.children()
    if kind_f == z3.Z3_OP_AND:
        if len(children) == 1:
            return z3BoolRef_to_SymPy(children[0])
        else:
            return [z3BoolRef_to_SymPy(ch) for ch in children]

    elif kind_f == z3.Z3_OP_OR:
        return [z3BoolRef_to_SymPy(ch) for ch in children]

    elif kind_f == z3.Z3_OP_EQ or kind_f == z3.Z3_OP_LE or kind_f == z3.Z3_OP_LT or kind_f == z3.Z3_OP_GE or kind_f == z3.Z3_OP_GT:
        # FIXME move constants to let 0 on one side
        if children[0].__str__() == '0':
            return sympify(re.sub("ToReal\((\d+)\)", r'\1', children[1].__str__()))
        else:
            return sympify(re.sub("ToReal\((\d+)\)", r'\1', children[0].__str__()))

    elif kind_f == z3.Z3_OP_NOT:
        if kind_subf == z3.Z3_OP_EQ:
            # FIXME
            return sympify(formula.__str__())
        elif kind_subf == z3.Z3_OP_UNINTERPRETED and subf.num_args()==0 :
            raise Exception("Found negation of boolean")
        else:
            raise Exception("negation is supported only for equalities")
    else:
        raise Exception("kind %s of subformula not supported" % decl_f)

def L2O(formula):

    formula = formula_to_BoolRef(formula)

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
        variables, dict_sym2z3_vars = get_vars_sym(formula)

    R = L2O(formula)

    return (R, make_lambda(R, variables, args))
