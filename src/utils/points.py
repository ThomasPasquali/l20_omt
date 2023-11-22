
from dataclasses import dataclass, field
import numpy as np

@dataclass(order=True)
class LocalMin:
    point: np.ndarray
    value: float


def sort_minima(list_of_minima):
    list_of_minima.sort(key=lambda minimum : minimum.value)
    return list_of_minima

def sort_dict_by_value(dict):
    return {k: v for k, v in sorted(dict.items(), key=lambda item: item[1])}

def sort_lits_wrt_value(literals_values):
    return sort_dict_by_value(literals_values)

def get_assignment(local_min, variables):
    assignment = {variables[i]: local_min.point[i] for i in range(len(variables))}
    return assignment

def printLocalMin(local_min):
    print("\nLocal min:\n\tPoint: %s\n\tValue: %s " %(local_min.point, local_min.value))

def printAssignment(assignment, dict_orig_name_vars):
    print("\nAssignment:")
    for var, value in assignment.items():   
        print("\tVar %s:\t\t%s " %(dict_orig_name_vars[var], value))