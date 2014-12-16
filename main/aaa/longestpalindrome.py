# -*- coding: utf-8 -*-
"""
A module for finding the longest (not contiguous) palindrome in a word
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'

def LP(S):
    """Find the longest palindrome subsequence in S"""
    T = [ [None]*len(S) for _ in range(len(S))]
    LP_aux(S, T, 0, len(S)-1)
    return T[0][len(S)-1]

def LP_aux(S, T, i, j):
    """
    Longest palindrome subsequence (not contiguous)
    S : string
    T : table to store the subproblem (must be of size len(S)xlen(S))
    i : the starting index
    j : the ending index
    """
    if T[i][j] is  None:
        if i > j:
            T[i][j] = ""
        elif i == j:
            T[i][j] = S[i]
        elif S[i] == S[j]:
            j_prime = j-1 if j > 0 else j
            T[i][j] = S[i]+LP_aux(S, T, i+1, j_prime)+S[j]
        else:
            left = len(LP_aux(S, T, i, j-1))
            right = len(LP_aux(S, T, i+1, j))
            T[i][j] = T[i+1][j]  if (left < right) else T[i][j-1]
    return T[i][j]


def LP_sparse(S):
    """Find the longest palindrome subsequence in S (sparse version)"""
    T = {}
    LP_sparse_aux(S, T, 0, len(S)-1)
    return T[(0, len(S)-1)]

def LP_sparse_aux(S, T, i, j):
    """
    Longest (none contiguous) palindrome subsequence 
    S : string
    T : table to store the subproblem (must be of size len(S)xlen(S))
    i : the starting index
    j : the ending index
    """
    if (i, j) not in  T:
        if i > j:
            T[(i, j)] = ""
        elif i == j:
            T[(i, j)] = S[i]
        elif S[i] == S[j]:
            j_prime = j-1 if j > 0 else j
            T[(i, j)] = S[i]+LP_sparse_aux(S, T, i+1, j_prime)+S[j]
        else:
            left = len(LP_sparse_aux(S, T, i, j-1))
            right = len(LP_sparse_aux(S, T, i+1, j))
            T[(i, j)] = T[(i+1, j)]  if (left < right) else T[(i, j-1)]
    return T[(i, j)]


if __name__ == "__main__":
    import argparse

    #----------Parsing command line args-----------#
    parser = argparse.ArgumentParser()
    parser.add_argument("word", 
                        help="The word in which to look for the longest palindrome subsequence")

    args = parser.parse_args()

    palindrome =  LP_sparse(args.word)
    print palindrome, "(size", len(palindrome),")"