# SPDX-License-Identifier: MIT
"""Exact comparison-encoding counts. Standard library only; no floating point.

Two independent methods:
* enumerate [n]^n and test sorted parking inequalities (small n only);
* collapse T runs, then assign values in increasing order to strict-poset minima.
"""

from collections import Counter, defaultdict
from functools import lru_cache
from itertools import product
import argparse
import json
from pathlib import Path
import time


def encoding(a):
    return ''.join('A' if x < y else 'D' if x > y else 'T'
                   for x, y in zip(a, a[1:]))


def brute_counts(n):
    answer = Counter()
    for a in product(range(1, n + 1), repeat=n):
        if all(b <= i for i, b in enumerate(sorted(a), 1)):
            answer[encoding(a)] += 1
    return answer


def collapse(w):
    weights = [1]
    directions = []
    for c in w:
        if c == 'T':
            weights[-1] += 1
        else:
            assert c in 'AD'
            directions.append(c)
            weights.append(1)
    return weights, directions


def poset_count(w, maximum=None):
    """F_n(w), optionally also bounding the largest value by maximum.

    A mask records T blocks already assigned numbers <= j-1. At value j,
    exactly an arbitrary subset of the minimal unassigned blocks may be
    selected; all strict predecessors must have been filled earlier. The
    cumulative weight must be >= j. Empty subsets are allowed.
    """
    weights, directions = collapse(w)
    n = sum(weights)
    m = len(weights)
    full = (1 << m) - 1
    predecessors = [0] * m
    for i, c in enumerate(directions):
        if c == 'A':
            predecessors[i + 1] |= 1 << i
        else:
            predecessors[i] |= 1 << (i + 1)
    mask_weight = [0] * (full + 1)
    for mask in range(1, full + 1):
        bit = mask & -mask
        mask_weight[mask] = mask_weight[mask ^ bit] + weights[bit.bit_length()-1]

    @lru_cache(None)
    def transitions(mask):
        available = 0
        for i, pred in enumerate(predecessors):
            if not mask & (1 << i) and pred & mask == pred:
                available |= 1 << i
        options = []
        subset = available
        while True:
            options.append(mask | subset)
            if subset == 0:
                break
            subset = (subset - 1) & available
        return options

    states = {0: 1}
    for j in range(1, (n if maximum is None else maximum) + 1):
        next_states = defaultdict(int)
        for mask, count in states.items():
            for target in transitions(mask):
                if mask_weight[target] >= j:
                    next_states[target] += count
        states = next_states
    return states.get(full, 0)


@lru_cache(None)
def content_weight(composition):
    """Number of valid distinct value choices for ordered multiplicities."""
    last_counts = {0: 1}
    previous_size = 0
    for size in composition:
        bound = previous_size + 1
        next_counts = {}
        prefix = 0
        for value in range(1, bound + 1):
            prefix += last_counts.get(value-1, 0)
            next_counts[value] = prefix
        last_counts = next_counts
        previous_size += size
    return sum(last_counts.values())


def ordered_partition_counts(n):
    """Enumerate ordered set partitions; weight by allowed value choices."""
    counts = Counter()
    values = [0] * n
    composition = []
    full = (1 << n) - 1

    def visit(remaining, level):
        if not remaining:
            counts[encoding(values)] += content_weight(tuple(composition))
            return
        subset = remaining
        while subset:
            bits = subset
            while bits:
                bit = bits & -bits
                values[bit.bit_length()-1] = level
                bits ^= bit
            composition.append(subset.bit_count())
            visit(remaining ^ subset, level + 1)
            composition.pop()
            subset = (subset - 1) & remaining

    visit(full, 1)
    return counts


def summarize(n, counts):
    best = max(counts.values())
    return {
        'n': n, 'maximum': best,
        'maximizers': sorted(w for w, count in counts.items() if count == best),
        'total': sum(counts.values()), 'number_of_encodings': len(counts),
        'top': sorted(counts.items(), key=lambda p: (-p[1], p[0]))[:12],
        'alternating_A': counts.get(''.join('AD'[i % 2] for i in range(n-1))),
        'alternating_D': counts.get(''.join('DA'[i % 2] for i in range(n-1))),
        'maximum_with_T': max((v for w, v in counts.items() if 'T' in w), default=0),
    }


def self_check(max_n=6):
    records = []
    for n in range(1, max_n+1):
        start = time.perf_counter()
        brute = brute_counts(n)
        partitions = ordered_partition_counts(n)
        assert brute == partitions, (n, 'brute vs partitions')
        assert sum(brute.values()) == (n+1)**(n-1)
        assert len(brute) == 3**(n-1)
        for w, expected in brute.items():
            observed = poset_count(w)
            assert observed == expected, (n, w, observed, expected)
        record = summarize(n, brute)
        record['seconds'] = time.perf_counter()-start
        record['all_three_methods_agree'] = True
        records.append(record)
        print(json.dumps(record), flush=True)
    return records


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', type=int)
    parser.add_argument('--partitions', type=int)
    parser.add_argument('--word')
    parser.add_argument('--output')
    args = parser.parse_args()
    if args.check is not None:
        result = self_check(args.check)
    elif args.partitions is not None:
        counts = ordered_partition_counts(args.partitions)
        result = summarize(args.partitions, counts)
        print(json.dumps(result), flush=True)
    elif args.word is not None:
        result = {'word': args.word, 'count': poset_count(args.word)}
        print(json.dumps(result), flush=True)
    else:
        parser.error('choose --check, --partitions, or --word')
    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
