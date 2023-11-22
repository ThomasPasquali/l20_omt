import z3
import sympy as sym


z3.set_option(max_args=10000000, max_lines=1000000, max_depth=10000000, max_visited=1000000)

def formula_to_BoolRef(formula):
    if isinstance(formula, z3.z3.AstVector):
        formula = z3.And(formula)
    if not isinstance(formula, z3.z3.BoolRef):
        raise TypeError("Wrong formula type: %s" % type(formula))
    return formula

class AstRefKey:
    def __init__(self, n):
        self.n = n
    def __hash__(self):
        return self.n.hash()
    def __eq__(self, other):
        return self.n.eq(other.n)
    def __repr__(self):
        return str(self.n)

def askey(n):
    assert isinstance(n, z3.AstRef)
    return AstRefKey(n)

def get_vars_z3_fast(f):
    r = set()
    def collect(f):
      if z3.is_const(f): 
          if f.decl().kind() == z3.Z3_OP_UNINTERPRETED and not f in r:
              r.add(f)
      else:
          for c in f.children():
              collect(c)
    collect(f)
    return r

def get_vars_z3(formula):
    return get_vars_z3_fast(formula)
    # return z3.z3util.get_vars(formula)    # this is slow


def get_vars_sym(formula, vars_z3=None):

    dict_sym2z3_vars = {}

    if not vars_z3:
        vars_z3 = get_vars_z3(formula)

    vars_sym = []

    for var_z3 in vars_z3:
        var_name = var_z3.__str__()
        var_sym = sym.symbols(var_name)
        vars_sym.append(var_sym)
        dict_sym2z3_vars[var_sym] = var_z3

    vars_sym = tuple(vars_sym)

    return vars_sym, dict_sym2z3_vars

def remove_pi_from_vars(variables):
    return list(filter(lambda var: var.name!="pi", variables))


def to_cnf(formula):
    formula = formula_to_BoolRef(formula)

    t_simplify = z3.Tactic('simplify' )
    t_tseitin_cnf = z3.Tactic('tseitin-cnf')
    t_to_cnf = z3.Then(t_simplify, "elim-and",  t_tseitin_cnf)
    new_formula = t_to_cnf(formula).as_expr()

    return new_formula


def is_not(formula):
    return formula.decl().kind() == z3.Z3_OP_NOT

def is_or(formula):
    return formula.decl().kind() == z3.Z3_OP_OR


def is_and(formula):
    return formula.decl().kind() == z3.Z3_OP_AND

def is_eq(formula):

    formula = formula_to_BoolRef(formula)

    decl_f = formula.decl()
    kind_f = decl_f.kind()

    return kind_f == z3.Z3_OP_EQ


def is_le(formula):

    formula = formula_to_BoolRef(formula)

    decl_f = formula.decl()
    kind_f = decl_f.kind()

    return kind_f == z3.Z3_OP_LE


def is_lt(formula):

    formula = formula_to_BoolRef(formula)

    decl_f = formula.decl()
    kind_f = decl_f.kind()

    return kind_f == z3.Z3_OP_LT


def is_ge(formula):

    formula = formula_to_BoolRef(formula)

    decl_f = formula.decl()
    kind_f = decl_f.kind()

    return kind_f == z3.Z3_OP_GE


def is_gt(formula):

    formula = formula_to_BoolRef(formula)

    decl_f = formula.decl()
    kind_f = decl_f.kind()

    return kind_f == z3.Z3_OP_GT


def ge2le(atom):
    if not is_ge(atom):
        raise Exception("The atom given is not in the ge form")

    atom = formula_to_BoolRef(atom)
    children = atom.children()
    new_atom = children[1] <= children[0]
    return new_atom


def gt2lt(atom):
    if not is_gt(atom):
        raise Exception("The atom given is not in the gt form")

    atom = formula_to_BoolRef(atom)
    children = atom.children()
    new_atom = children[1] < children[0]
    return new_atom

def create_bool2_real_vars(vars_z3):
    x = z3.Real('x')
    b2r_vars = []
    dict_b2r_vars = {}
    dict_r2b_vars = {}
    for var in vars_z3:
        if var.sort().is_bool():
            b2r_var = z3.Real("b2r_"+var.__str__())
            b2r_vars.append(b2r_var)
            dict_b2r_vars[var] = b2r_var
            dict_r2b_vars[b2r_var] = var
        else:
            dict_b2r_vars[var] = var
            dict_r2b_vars[var] = var
    return b2r_vars, dict_b2r_vars, dict_r2b_vars

def formula_bool2real(formula, dict_b2r_vars):
    # assumes formula is in cnf
    decl_f = formula.decl()
    kind_f = decl_f.kind()
    name_f = decl_f.name()
    children = formula.children()
    
    if kind_f == z3.Z3_OP_AND:
        return z3.And([formula_bool2real(ch, dict_b2r_vars) for ch in children])
    elif kind_f == z3.Z3_OP_OR:
        return z3.Or([formula_bool2real(ch, dict_b2r_vars) for ch in children])
    elif kind_f == z3.Z3_OP_UNINTERPRETED:
        if formula.num_args() == 0:
            return dict_b2r_vars[formula] >= 1
        else:
            raise Exception("Formula not supported: ", formula)
    elif kind_f == z3.Z3_OP_NOT:    
        subf = formula.children()[0]
        decl_subf = subf.decl()
        kind_subf = decl_subf.kind()
        if kind_subf in [z3.Z3_OP_LE, z3.Z3_OP_LT, z3.Z3_OP_GE, z3.Z3_OP_GT, z3.Z3_OP_EQ]:
            return formula
        elif kind_subf == z3.Z3_OP_UNINTERPRETED and subf.num_args()==0 :
            return dict_b2r_vars[subf] <= -1
        else:
            raise Exception("Negation not supported: ", formula)
    elif kind_f in [z3.Z3_OP_LE, z3.Z3_OP_LT, z3.Z3_OP_GE, z3.Z3_OP_GT, z3.Z3_OP_EQ]:
        return formula
    else:
        raise Exception("Formula not supported: ", formula)


def bool2real(formula, vars_z3):
    formula = formula_to_BoolRef(formula)
    new_b2r_vars, dict_b2r_vars, dict_r2b_vars = create_bool2_real_vars(vars_z3)
    formula = formula_bool2real(formula, dict_b2r_vars)
    return formula, new_b2r_vars, dict_r2b_vars

# Warning: does not distribute not(a == b) ; negation of eqs are treated separately
def distribute_not(formula):
    # assumes formula is in cnf
    decl_f = formula.decl()
    kind_f = decl_f.kind()
    name_f = decl_f.name()
    children = formula.children()
    
    if kind_f == z3.Z3_OP_AND:
        return z3.And([distribute_not(ch) for ch in children])
    elif kind_f == z3.Z3_OP_OR:
        return z3.Or([distribute_not(ch) for ch in children])
    elif kind_f == z3.Z3_OP_UNINTERPRETED:
        return formula
    elif kind_f == z3.Z3_OP_NOT:    
        subf = formula.children()[0]
        decl_subf = subf.decl()
        kind_subf = decl_subf.kind()
        if kind_subf in [z3.Z3_OP_LE, z3.Z3_OP_LT, z3.Z3_OP_GE, z3.Z3_OP_GT, z3.Z3_OP_EQ]:
            op0, op1 = subf.children()
            if is_ge(subf):
                return op0 < op1
            elif is_gt(subf):
                return op0 <= op1
            elif is_le(subf):
                return op1 < op0
            elif is_lt(subf):
                return op1 <= op0
            elif is_eq(subf):
                return z3.Not(subf)
            else:        
                raise Exception("Given atom is in the wrong form") 
        elif kind_subf == z3.Z3_OP_UNINTERPRETED and subf.num_args()==0 :
            return formula
        else:
            raise Exception("Negation not supported: ", formula)
    elif kind_f in [z3.Z3_OP_LE, z3.Z3_OP_LT, z3.Z3_OP_GE, z3.Z3_OP_GT, z3.Z3_OP_EQ]:
        return formula
    else:
        raise Exception("Formula not supported: ", formula)
