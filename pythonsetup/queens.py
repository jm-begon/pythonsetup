# -*- coding: utf-8 -*-
"""
The :mod:`queens` module solves brute-forcely the N-queens problem.
The board is encoded as a state vector...
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'

from itertools import permutations
import sys

def check_queen(B):
    """Check whether the N-queens problem is solved or not"""
    line = [False]*len(B)
    for i in range(len(B)):
        if line[B[i]]:
            return False
        line[B[i]] = True
    diag1 = [False]*(len(B)*2)
    diag2 = [False]*(len(B)*2)
    for i in range(len(B)):
        d1 = B[i] - i + len(B)
        d2 = B[i] + i - 1
        if diag1[d1] or diag2[d2]:
            return False
        diag1[d1] = True
        diag2[d2] = True
    return True

def print_queen(B):
    """Prints the board"""
    N = len(B)    
    for i in range(N):
        print
        sys.stdout.write("+")
        for k in range(N):
            sys.stdout.write("---+")
        print
        sys.stdout.write("|")
        for j in range(N):
            if B[j] == i:
                sys.stdout.write(" x ")
            else:
                sys.stdout.write("   ")
            sys.stdout.write("|")
    print
    sys.stdout.write("+")
    for k in range(N):
        sys.stdout.write("---+")

#----------------------Generate all configurations---------------
def inc_queen(B, p):
    """Increment the queen state vector"""
    B[p] += 1
    if B[p] >= len(B):
        B[p] = 0
        if p == 0:
            return False
        return inc_queen(B, p-1)
    return True


def queen(N):
    """Generator for N-queens problem (all configuration)"""
    B = [0]*N
    while inc_queen(B, N-1):
        if check_queen(B):
            yield B


#----------------------Generate only the permutations------------

def queen_permut(N):
    """Generator for the N-queens problem (permutation only)"""
    for B in permutations(range(N)):
        if check_queen(B):
            yield B


#------------------------Only yield the number of solutions----------
def nb_solutions(N):
    """Return the number of solutions for the size N"""
    nb = 0
    for B in permutations(range(N)):
        if check_queen(B):
            nb += 1
    return nb


if __name__ == "__main__":
    import argparse

    MAX_NB_SOLUTION = 100*100

    parser = argparse.ArgumentParser("Compute the solutions to the N-queens problem (brute-force)")
    parser.add_argument("N",
                        type=int, 
                        help="The size of the board")
    parser.add_argument("-s", "--slow",
                        action="store_true",
                        help="Proceeds by testing all the N**N possibilites")
    parser.add_argument("-n", "--number",
                        type=int,
                        help="The number of solution to print",
                        default=MAX_NB_SOLUTION) # TODO : do better
    args = parser.parse_args()
    N = args.N
    if args.slow:
        gen = queen
    else:
        gen = queen_permut
    
    nb = 0
    for board in gen(N):
        print_queen(board)
        print
        nb+=1
        if nb >= args.number:
            break

    if args.number == MAX_NB_SOLUTION:
        print "There are", nb, "solution for the", N, "- queens problem" 