"""
sudoku_solver.py

Implement the function `solve_sudoku(grid: List[List[int]]) -> List[List[int]]` using a SAT solver from PySAT.
"""

from pysat.formula import CNF
from pysat.solvers import Solver
from typing import List

def solve_sudoku(grid: List[List[int]]) -> List[List[int]]:
    """Solves a Sudoku puzzle using a SAT solver. Input is a 2D grid with 0s for blanks."""

    # TODO: implement encoding and solving using PySAT 
    cnf = CNF()
    for i in range(9):
        for j in range(9):
            if grid[i][j]!=0:
# appended already given values in the puzzle
                cnf.append([81*i+9*j+grid[i][j]]) 
    for i in range(9):
        for j in range(9):
            L = []
            for k in range(9):
                L.append(81*i+9*j+k+1)
            cnf.append(L)
    for i in range(9):
        for j in range(9):
            for k1 in range(9):
                for k2 in range(k1+1,9):
                    # value cannot start from 0 so added 1
                    cnf.append([-(81*i+9*j+k1+1), -(81*i+9*j+k2+1)])
    for i in range(9):
        for k in range(9):
            L = []
            for j in range(9):
                L.append(81*i+9*j+k+1)
            cnf.append(L)
    for j in range(9):
        for k in range(9):
            L = []
            for i in range(9):
                L.append(81*i+9*j+k+1)
            cnf.append(L)
    for i in range(0, 7, 3):
        for j in range(0, 7 , 3):
            for k in range(9):
                L=[]
                for di in range(3):
                    for dj in range(3):
                        L.append(81*(i+di)+9*(j+dj)+k+1)
                cnf.append(L)
    result = []
    for i in range(9):
        L = []
        for j in range(9):
            L.append(0)
        result.append(L)
    with Solver(name='glucose3') as solver:
        solver.append_formula(cnf.clauses)
        if solver.solve():
            model = solver.get_model()
            #Filling grid from obtained satisfying assignment
            for num in model:
                if(num>0):
                    num-=1
                    k = (num%9)+1
                    j = (num//9)%9
                    i = (num//81)
                    result[i][j] = k
            return result
        else:
            return []