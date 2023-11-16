# Search candidate approximate solutions

This tool translates an SMT problem into a numerical minimization one. Then it generates candidate approximate solutions of the original problem. 

Theories supported : 
- Non-linear Real Arithmetic (NRA)
- Non-linear Transcendental Arithmetic (NTA)

## Dependencies
- Python3 (3.10.12)
- Python packages:
-- z3-solver   (4.12.1.0)
-- sympy       (1.11.1)
-- scipy       (1.9.1)
-- numpy       (1.23.3)

## How to run
From the main folder:

  ```python3 src/search_solutions.py examples/test.smt2```
