# SPDX-License-Identifier: MIT
"""Constructive elimination of ties, with a fixed target for each encoding.

This is an injection on each encoding class; it is not asserted to be
injective across different source encodings.
"""

from collections import defaultdict
from itertools import product
from pathlib import Path
import json
from exact_counts import encoding
from rotation_injection import is_parking


def plan_step(w):
    i = w.rfind('T')
    assert i >= 0
    if i == len(w)-1:
        return {'kind':'end','start':i,'target':w[:i]+'A'}
    if w[i+1] == 'D':
        return {'kind':'next_D','start':i,
                'target':w[:i]+'A'+w[i+1:]}
    assert w[i+1] == 'A'
    end = i+2
    while end < len(w) and w[end] != w[end-1]:
        assert w[end] in 'AD'
        end += 1
    q = w[i+1:end]
    return {'kind':'A_tail' if q[-1]=='A' else 'D_tail',
            'start':i,'end':end,'alternating_tail':q,
            'target':w[:i]+q+('D' if q[-1]=='A' else 'A')+w[end:]}


def forward_step(a, plan):
    a = tuple(a)
    i = plan['start']
    kind = plan['kind']
    if kind == 'repair_AA_end':
        return a[:-2] + (a[-1],a[-2])
    if kind in ('end','next_D'):
        b = list(a)
        b[i+1] += 1
        return tuple(b)
    end = plan['end']
    segment = a[i:end+1]
    x = segment[0]
    assert x == segment[1]
    if kind == 'A_tail':
        segment_out = (x,) + segment[2:] + (min(x,segment[-2]),)
    else:
        u = segment[-1]
        if u < x:
            segment_out = (x,) + segment[2:] + (x,)
        elif u > x:
            segment_out = (x,u,x) + segment[2:-1]
        else:
            segment_out = (x,) + segment[2:-1] + (x,x+1)
    return a[:i] + segment_out + a[end+1:]


def inverse_step(b, plan):
    b = tuple(b)
    i = plan['start']
    kind = plan['kind']
    if kind == 'repair_AA_end':
        return b[:-2] + (b[-1],b[-2])
    if kind in ('end','next_D'):
        a = list(b)
        a[i+1] -= 1
        return tuple(a)
    end = plan['end']
    s = b[i:end+1]
    x = s[0]
    if kind == 'A_tail':
        original = (x,x) + s[1:-1]
    elif s[-1] == x:
        original = (x,x) + s[1:-1]
    elif s[1] < s[-1]:
        original = (x,x) + s[3:] + (s[1],)
    else:
        original = (x,x) + s[1:-2] + (x,)
    return b[:i] + original + b[end+1:]


def eliminate_encoding(w, strict=True):
    had_tie = 'T' in w
    plans=[]
    while 'T' in w:
        plan=plan_step(w)
        plans.append(plan)
        w=plan['target']
    if strict and had_tie and len(w)>=2 and w.endswith('AA'):
        plan={'kind':'repair_AA_end','start':len(w)-2,
              'target':w[:-1]+'D'}
        plans.append(plan)
        w=plan['target']
    return w,plans


def eliminate_word(a):
    w=encoding(a)
    target,plans=eliminate_encoding(w)
    b=tuple(a)
    for plan in plans:
        b=forward_step(b,plan)
    return b,target,plans


def verify(max_n=6):
    records=[]
    for n in range(1,max_n+1):
        images=defaultdict(set)
        checked=0
        steps=0
        branch_counts=defaultdict(int)
        for a in product(range(1,n+1),repeat=n):
            w=encoding(a)
            if 'T' not in w or not is_parking(a):
                continue
            checked+=1
            b,target,plans=eliminate_word(a)
            assert encoding(b)==target, (a,b,w,target)
            assert 'T' not in target
            assert is_parking(b), (a,b)
            assert b not in images[w], (a,b,w)
            images[w].add(b)
            current=a
            for plan in plans:
                branch_counts[plan['kind']]+=1
                steps+=1
                nxt=forward_step(current,plan)
                assert encoding(nxt)==plan['target'], (current,nxt,plan)
                assert is_parking(nxt), (current,nxt,plan)
                assert inverse_step(nxt,plan)==current, (current,nxt,plan)
                current=nxt
        r={'n':n,'parking_functions_with_ties_checked':checked,
           'individual_steps_checked':steps,
           'branches':dict(branch_counts),
           'all_inverses_encodings_and_parking_checks_pass':True}
        records.append(r)
        print(json.dumps(r),flush=True)
    comparisons=[]
    for n in range(1,11):
        c=json.loads(Path(f'proof_artifacts/counts_n{n}.json').read_text())
        amount=0
        for w,v in c.items():
            if 'T' in w:
                target,_=eliminate_encoding(w)
                assert c[target]>=v, (n,w,target,v,c[target])
                if n>=3:
                    assert c[target]>v, (n,w,target,v,c[target])
                amount+=1
        comparisons.append({'n':n,'encoding_class_inequalities_checked':amount,
                            'strict_for_every_tied_encoding_if_n_ge_3':True})
    return {'actual_word_checks':records,'complete_count_checks':comparisons}


if __name__ == '__main__':
    result=verify()
    Path('proof_artifacts/tie_elimination_audit.json').write_text(
        json.dumps(result,indent=2)+'\n',encoding='utf-8')
