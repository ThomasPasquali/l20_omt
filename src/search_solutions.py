import argparse
from parser.parser import formula_from_text
from utils.logic import get_vars, get_vars_z3, to_cnf, distribute_not, bool2real, sanitize_var_names, remove_pi_from_vars
from optimizer_interface import search_candidate_approximate_solutions
from utils.points import sort_minima, printAssignment, printLocalMin

import time

def main(args):
    text = open(args.smt2_file,"r").read()

    formula = formula_from_text(text)
    formula = to_cnf(formula)

    vars_z3 = get_vars_z3(formula)
     
    formula, new_vars_list = sanitize_var_names(formula, vars_z3) # Sympy does not accept '!', '@', and '.' in variables names
    formula, new_b2r_vars = bool2real(formula, new_vars_list)
    formula = distribute_not(formula) 

    vars_sym = get_vars(formula)
    vars_sym = remove_pi_from_vars(vars_sym)
    #print("variables:", vars_sym)

    local_mins = search_candidate_approximate_solutions(args, formula, vars_sym)
    local_mins = sort_minima(local_mins)

    for local_min in local_mins:
        point = local_min.point
        assignment = {vars_sym[i]: point[i] for i in range(len(vars_sym))}
        #print("\n")
        #printLocalMin(local_min)
        #printAssignment(assignment)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(prog='')
    parser.add_argument('smt2_file', help='specify the smt2 file to analyze.')
    parser.add_argument ('--niter', help='number of basin hopping iterations', action='store', required=False, type=int, default=3)
    parser.add_argument ('--stepsize', help='maximum step size for basin hopping random jump', action='store', required=False, type=int, default=10)

    args= parser.parse_args()   
    
    main(args)