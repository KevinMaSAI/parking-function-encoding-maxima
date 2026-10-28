# SPDX-License-Identifier: MIT
"""Exact answer to Problem 54, using the proved maximizing encodings."""
import argparse
import json
from exact_counts import poset_count


def maximizing_encodings(n):
    if n<1:raise ValueError('n must be positive')
    if n==1:return ['']
    if n==2:return ['A','D','T']
    up=''.join('AD'[i%2] for i in range(n-1))
    if n%2:return [up]
    down=''.join('DA'[i%2] for i in range(n-1))
    return [up,down]


def solve(n):
    words=maximizing_encodings(n)
    return {'n':n,'maximizers':words,'maximum':poset_count(words[0])}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('n',type=int)
    parser.add_argument('--table',action='store_true',help='print rows 1 through n')
    args=parser.parse_args()
    for n in range(1,args.n+1) if args.table else [args.n]:
        print(json.dumps(solve(n)),flush=True)
