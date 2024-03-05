#!/usr/bin/env python
from random import seed
import numpy as np
import scipy.optimize as op
from sympy import *
from pprint import pprint
from loguru import logger as log
import re

from datetime import datetime

from utils.logic import get_vars_sym, formula_to_BoolRef

from L2O import L2O_lambda, z3BoolRef_to_SymPy, z3BoolRef_to_LaTex, make_lambda

from utils.points import LocalMin
from utils.plots import plot_2d

def _callback_global(x, f, accepted):
    local_min = LocalMin(x, f)
    local_mins.append(local_min)
    print(local_min)
    return False

def run_basinhopping(args, L, dim, starting_point=None):
    global local_mins
    local_mins = []

    if not starting_point:
        starting_point = np.zeros(dim)

    #print("\nstarting_point: ",starting_point)
    #print("\nL(%s):" %starting_point, L(starting_point))

    res = op.basinhopping(L, starting_point,
                          niter=args.niter, stepsize=args.stepsize,
                          minimizer_kwargs={"method": 'powell'},
                          callback=_callback_global,
                          seed=165721
                          )
    return local_mins


def search_candidate_approximate_solutions(args, original_formula, formula, cost, variables=None, var_names=None):

    orig_variables, orig_var_names = get_vars_sym(original_formula)
    dim = len(variables)
    formula = formula_to_BoolRef(formula)

    COST = z3BoolRef_to_SymPy(cost)

    functions = z3BoolRef_to_SymPy(original_formula)
    log.debug(f"Original assertions:")
    for f in functions:
        pretty_print(f)
        print()
    L20, L20_lambda = L2O_lambda(args, formula, variables)
    L20 = L20.subs({k: Symbol(str(v)) for k, v in var_names.items()})
    # init_printing(use_latex=True, pretty_print=True, latex_mode='equation')
    # log.debug(type(R))
    # log.debug(variables)
    # log.debug(var_names)
    log.debug(f"L2O formula:")
    pretty_print(L20)
    # preview(R, output='png')
    log.debug(f"COST:")
    print(type(COST))
    pretty_print(COST)

    DOM_INF = -15
    DOM_SUP = 15
    N_POINTS = 1000
    X = np.linspace(DOM_INF, DOM_SUP, N_POINTS)
    # Y = np.linspace(DOM_INF, DOM_SUP, N_POINTS)
    # Z = np.linspace(DOM_INF, DOM_SUP, N_POINTS)
    
    local_mins = run_basinhopping(args, L20_lambda, dim)
    print(orig_variables)

    plot_2d(
        X,
        orig_variables,
        {k: Symbol(str(v)) for k, v in orig_var_names.items()},
        L20_lambda,
        lambdify(orig_variables, COST, 'scipy'),
        functions,
        np.array([m.point[0] for m in local_mins]), np.array([m.value for m in local_mins]),
        z3BoolRef_to_LaTex(original_formula, {k: Symbol(str(v)) for k, v in var_names.items()})
            + '\quad COST=' + latex(COST)
            + ' '.join([f'\qquad f_{i}=' 
            + latex(f.subs({k: Symbol(str(v)) for k, v in orig_var_names.items()})) for i, f in enumerate(functions)])
            + '\quad \mathcal{L2O}(\phi)=' + latex(L20)
    )

    return local_mins
