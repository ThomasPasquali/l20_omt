#!/usr/bin/env python
from random import seed
import numpy as np
import scipy.optimize as op

from datetime import datetime
from pprint import pprint

from utils.logic import get_vars, formula_to_BoolRef

from L2O import L2O_lambda

from utils.points import LocalMin

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


def search_candidate_approximate_solutions(args, formula, variables=None):

    if not variables:
        variables = get_vars(formula)
    dim = len(variables)
    formula = formula_to_BoolRef(formula)

    L = L2O_lambda(formula, variables)

    local_mins = run_basinhopping(args, L, dim)

    return local_mins
