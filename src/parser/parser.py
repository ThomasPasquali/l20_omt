
import z3
from utils.logic import formula_to_BoolRef
import re

def formula_from_text(text):
    text = re.sub(';.*\n', '', text)
    text = fix_transcendental_decl_for_z3(text)
    print(text)

    # FIXME exctract cost if not only in minimize/maximize clause
    cost = re.findall('\((minimize|maximize) (.*)\)', text)
    if cost and cost[0] and cost[0][1]:
        decl = " ".join(re.findall("\(declare.*\)", text))
        print(f'{decl} (assert (< 0 {cost[0][1]}))')
        cost = z3.parse_smt2_string(f'{decl} (assert (> {cost[0][1]} 0))')
    else:
        cost = None

    formula = z3.parse_smt2_string(text)
    if isinstance(formula, z3.z3.AstVector): 
        formula = z3.And(formula)
    if not isinstance(formula, z3.z3.BoolRef):
        raise TypeError(f"Type {type(formula)} not supported")
    
    return formula, cost

def fix_transcendental_decl_for_z3(text):
    #print(f"\noriginal text: {text}")
    if "(exp " in text and not "(declare-fun exp " in text:
        text = text.replace("(declare-fun", "(declare-fun exp (Real) Real)\n(declare-fun", 1)

    if "(log " in text and not "(declare-fun log " in text:
        text = text.replace("(declare-fun", "(declare-fun log (Real) Real)\n(declare-fun", 1)

    if "(arcsin " in text and not "(declare-fun arcsin " in text \
        or "(asin " in text and not "(declare-fun asin " in text:
        text = text.replace("(declare-fun", "(declare-fun asin (Real) Real)\n(declare-fun", 1)

    if "(arccos " in text and not "(declare-fun arccos " in text \
        or "(acos " in text and not "(declare-fun acos " in text:
        text = text.replace("(declare-fun", "(declare-fun acos (Real) Real)\n(declare-fun", 1)

    if "(arctan " in text and not "(declare-fun arctan " in text \
        or "(atan " in text and not "(declare-fun atan " in text:
        text = text.replace("(declare-fun", "(declare-fun atan (Real) Real)\n(declare-fun", 1)

    if "(arctan2 " in text and not "(declare-fun arctan2 " in text \
        or "(atan2 " in text and not "(declare-fun atan2 " in text:
        text = text.replace("(declare-fun", "(declare-fun atan2 (Real Real) Real)\n(declare-fun", 1)

    if "(power " in text:
        text = text.replace("(power ", "(pow ")

    if "pow " in text and not "(declare-fun pow " in text:
        text = text.replace("(declare-fun", "(declare-fun pow (Real Real) Real)\n(declare-fun", 1)

    if "(^ " in text or " ^ " in text and not "(declare-fun ^" in text:
        text = text.replace("(declare-fun", "(declare-fun pow (Real Real) Real)\n(declare-fun", 1)
        text = text.replace("^", "power")

    if "(sin" in text and not "(declare-fun sin" in text:
        text = text.replace("(declare-fun", "(declare-fun sin (Real) Real)\n(declare-fun", 1)

    if "(cos" in text and not "(declare-fun cos" in text:
        text = text.replace("(declare-fun", "(declare-fun cos (Real) Real)\n(declare-fun", 1)

    if "(tan" in text and not "(declare-fun tan" in text:
        text = text.replace("(declare-fun", "(declare-fun tan (Real) Real)\n(declare-fun", 1)

    if "(tanh" in text and not "(declare-fun tanh" in text:
        text = text.replace("(declare-fun", "(declare-fun tanh (Real) Real)\n(declare-fun", 1)

    if ("(pi" in text or "pi)" in text or " pi " in text) and not "(declare-fun pi" in text:
        text = text.replace("(declare-fun", "(declare-fun pi () Real)\n(declare-fun", 1)

    text = text.replace("power", "pow")
    text = text.replace("arctan", "atan")
    text = text.replace("arccos", "acos")
    text = text.replace("arcsin", "asin")
    #print(f"\nfixed text: {text}")

    return text


def list_of_transcendental_functions():
    return ["pi", "exp", "log",  "power",
            "arcsin", "arccos", "arctan", "arctan2",
            "sin", "cos", "tan", "tanh"]


def create_new_var_names(vars_z3):
    new_vars_list = []
    map_renamed_vars = []
    dict_renamed_vars = {}
    for i, var in enumerate(vars_z3):
        if var.__str__() == "pi":
            new_var_name = "pi"
        else:
            new_var_name = f"var_{i}"
        if z3.is_real(var):
            new_var = z3.Real(new_var_name)
        elif z3.is_bool(var):
            new_var = z3.Bool(new_var_name)
        else: 
            raise Exception("Unsupported kind for ", var)
        new_vars_list.append(new_var)
        map_renamed_vars.append((var, new_var))
        dict_renamed_vars[new_var] = var
    return new_vars_list, map_renamed_vars, dict_renamed_vars


def rename_variables(formula, vars_z3):
    formula = formula_to_BoolRef(formula)
    new_vars_list, map_renamed_vars, dict_renamed_vars = create_new_var_names(vars_z3)
    formula = z3.substitute(formula, map_renamed_vars)
    return formula, new_vars_list, dict_renamed_vars

def get_dict_original_names_vars(vars_sym, dict_sym2z3_vars, dict_r2b_vars, dict_renamed_vars):
    dict_vars = {}
    for var in vars_sym:
        dict_vars[var] = dict_renamed_vars[dict_r2b_vars[dict_sym2z3_vars[var]]]
    return dict_vars
