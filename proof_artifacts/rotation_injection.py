# SPDX-License-Identifier: MIT
"""Explicit injection: odd peak-ended alternating words -> valley-ended.

Every image has its final value strictly decreased. The multiset is either
unchanged, or one large value is replaced by a smaller one. Consequently the
map also preserves every symmetric coordinatewise downset, including PF_n,
even when applied to just an initial segment.
"""

from itertools import product
from pathlib import Path
import json
from exact_counts import encoding


def peak_to_valley(a):
    a = tuple(a)
    k = len(a)
    assert k >= 3 and k % 2 == 1
    assert encoding(a) == 'DA' * (k // 2)
    if a[0] < a[-1]:
        return a[1:] + a[:1]
    if a[0] > a[-1]:
        return a[-1:] + a[:-1]
    return a[1:-1] + (a[0], a[1])


def inverse_on_image(b):
    b = tuple(b)
    if b[0] < b[-1]:
        return b[-1:] + b[:-1]
    if b[0] > b[-1]:
        return b[1:] + b[:1]
    return b[-2:-1] + b[:-2] + b[-2:-1]


def is_parking(a):
    return all(value <= rank for rank, value in enumerate(sorted(a), 1))


def verify(max_k=9, alphabet=4):
    result = []
    for k in range(3, max_k+1, 2):
        images = set()
        inputs = 0
        for a in product(range(1, alphabet+1), repeat=k):
            if encoding(a) != 'DA'*(k//2):
                continue
            inputs += 1
            b = peak_to_valley(a)
            assert encoding(b) == 'AD'*(k//2), (a,b)
            assert b[-1] < a[-1], (a,b)
            assert all(x <= y for x,y in zip(sorted(b),sorted(a))), (a,b)
            assert inverse_on_image(b) == a, (a,b)
            assert b not in images, (a,b)
            images.add(b)
        witness = (1,2)*(k//2-1)+(1,k,1)
        assert len(witness) == k
        assert encoding(witness) == 'AD'*(k//2)
        assert is_parking(witness)
        nonparking_preimage = inverse_on_image(witness)
        assert not is_parking(nonparking_preimage)
        assert nonparking_preimage.count(k) == 2
        record = {'length':k, 'alphabet':alphabet, 'inputs_checked':inputs,
                  'injection_verified':True,
                  'strictness_witness':witness,
                  'inverse_is_not_parking':nonparking_preimage}
        print(json.dumps(record),flush=True)
        result.append(record)
    return result


if __name__ == '__main__':
    Path('proof_artifacts/rotation_injection_audit.json').write_text(
        json.dumps(verify(),indent=2)+'\n',encoding='utf-8')
