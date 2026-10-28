# SPDX-License-Identifier: MIT
"""First-defect injection, proving the strict binary maximum theorem.

The target flips the alternating prefix ending at the middle vertex of
the first AA or DD. The right boundary is preserved. Every step removes
exactly one defect. See the full proof note for unbounded-n justification.
"""
from collections import defaultdict
from itertools import product
from pathlib import Path
import argparse
import json
from exact_counts import encoding
from rotation_injection import peak_to_valley, inverse_on_image, is_parking
from odd_prefix_repairs import valley_to_peak_above, inverse_threshold_image
from eliminate_ties import eliminate_encoding, forward_step as forward_tie


def defect_count(w):
    return sum(x==y for x,y in zip(w,w[1:]))


def plan_step(w):
    assert 'T' not in w
    i=next((i for i in range(len(w)-1) if w[i]==w[i+1]),None)
    assert i is not None
    k=i+2
    target=''.join('D' if x=='A' else 'A' for x in w[:k-1])+w[k-1:]
    assert defect_count(target)==defect_count(w)-1
    return {'length':k,'direction':w[i],'target':target}


def reverse_interior(a):
    return a[:1]+a[-2:0:-1]+a[-1:]


def forward_step(a,plan):
    a=tuple(a)
    k=plan['length']
    t=a[k]
    s=a[:k]
    direction=plan['direction']
    if k%2:
        b=peak_to_valley(s) if direction=='A' else valley_to_peak_above(s,t)
    elif direction=='A':
        b=s[::-1] if s[0]<t else reverse_interior(s)
    else:
        b=s[::-1] if s[0]>t else reverse_interior(s)
    return b+a[k:]


def inverse_step(b,plan):
    b=tuple(b)
    k=plan['length']
    t=b[k]
    s=b[:k]
    direction=plan['direction']
    if k%2:
        a=inverse_on_image(s) if direction=='A' else inverse_threshold_image(s,t)
    elif direction=='A':
        a=s[::-1] if s[0]<t else reverse_interior(s)
    else:
        a=s[::-1] if s[0]>t else reverse_interior(s)
    return a+b[k:]


def binary_plan(w):
    plans=[]
    while defect_count(w):
        p=plan_step(w)
        plans.append(p)
        w=p['target']
    return w,plans


def forward_binary(a):
    a=tuple(a)
    target,plans=binary_plan(encoding(a))
    b=a
    for p in plans:b=forward_step(b,p)
    return b,target,plans


def order_assignment(w, equal_groups=(), minimum=None, maximum=None):
    """Construct a rank-labelled witness for the strictness proof.

    Indices are zero-based. A designated singleton maximum may receive n
    instead of the number of merged blocks; all other ranks are consecutive.
    """
    n=len(w)+1
    parent=list(range(n))
    def find(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]];i=parent[i]
        return i
    for group in equal_groups:
        root=find(group[0])
        for i in group[1:]:parent[find(i)]=root
    roots=sorted(set(find(i) for i in range(n)))
    pred={r:set() for r in roots}
    for i,c in enumerate(w):
        low,high=(i,i+1) if c=='A' else (i+1,i)
        low,high=find(low),find(high)
        assert low!=high
        pred[high].add(low)
    lo=find(minimum) if minimum is not None else None
    hi=find(maximum) if maximum is not None else None
    order=[];remaining=set(roots)
    while remaining:
        candidates=[r for r in remaining if not (pred[r]&remaining)]
        assert candidates,'cycle in witness order'
        if lo is not None and not order:
            assert lo in candidates;choice=lo
        else:
            other=[r for r in candidates if r!=hi]
            choice=min(other) if other else hi
            assert choice is not None
        remaining.remove(choice);order.append(choice)
    if hi is not None:assert order[-1]==hi
    values={r:j+1 for j,r in enumerate(order)}
    if hi is not None:
        assert sum(find(i)==hi for i in range(n))==1
        values[hi]=n
    a=tuple(values[find(i)] for i in range(n))
    assert encoding(a)==w and is_parking(a),(w,a)
    return a


def missing_image_witness(w,plan):
    """For every defect step, construct a PF in the target outside its image."""
    k=plan['length'];direction=plan['direction'];target=plan['target']
    if k%2==0 and direction=='A':
        b=order_assignment(target,minimum=k-1,maximum=0)
        assert b[0]>=b[k]
        bad=inverse_step(b,plan)
        assert encoding(bad)!=w
    elif k%2==0:
        b=order_assignment(target,minimum=0,maximum=k-1)
        assert b[0]<=b[k]
        bad=inverse_step(b,plan)
        assert encoding(bad)!=w
    elif direction=='A':
        b=order_assignment(target,equal_groups=((0,k-1),),minimum=0,maximum=k-2)
        bad=inverse_step(b,plan)
        assert bad.count(len(w)+1)==2 and not is_parking(bad)
    else:
        b=order_assignment(target,equal_groups=((0,k-1),))
        assert b[0]==b[k-1]
        # Every image of the threshold injection has distinct prefix endpoints.
        bad=None
    return b,bad


def verify(max_n=6):
    word_records=[]
    for n in range(3,max_n+1):
        images=defaultdict(set);steps=0;inputs=0;branches=defaultdict(int)
        for a in product(range(1,n+1),repeat=n):
            w=encoding(a)
            if 'T' in w or not defect_count(w) or not is_parking(a):continue
            inputs+=1
            b,target,plans=forward_binary(a)
            assert encoding(b)==target and not defect_count(target)
            assert is_parking(b)
            assert b not in images[w],(w,a,b)
            images[w].add(b)
            current=a
            for p in plans:
                nxt=forward_step(current,p)
                assert encoding(nxt)==p['target']
                assert inverse_step(nxt,p)==current,(current,nxt,p)
                assert is_parking(nxt)
                assert all(x<=y for x,y in zip(sorted(nxt),sorted(current)))
                branches[f"{'odd' if p['length']%2 else 'even'}_{p['direction']}"]+=1
                current=nxt;steps+=1
        r={'n':n,'nonalternating_tieless_parking_functions':inputs,
           'steps_checked':steps,'branches':dict(branches),'all_checks_pass':True}
        print(json.dumps(r),flush=True);word_records.append(r)
    counts_records=[];witness_records=[]
    for n in range(3,11):
        counts=json.loads(Path(f'proof_artifacts/counts_n{n}.json').read_text())
        checked=0;witnesses=0
        for w,v in counts.items():
            if 'T' in w or not defect_count(w):continue
            p=plan_step(w);assert counts[p['target']]>v,(n,w,p)
            target,_=binary_plan(w);assert counts[target]>v
            b,bad=missing_image_witness(w,p)
            assert encoding(b)==p['target'] and is_parking(b)
            checked+=1;witnesses+=1
        r={'n':n,'strict_step_and_global_count_checks':checked,
           'missing_image_witnesses_checked':witnesses}
        print(json.dumps(r),flush=True);counts_records.append(r)
    return {'actual_word_checks':word_records,'all_binary_class_checks':counts_records}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',type=int,default=6)
    args=parser.parse_args()
    Path('proof_artifacts/binary_maximum_injection_audit.json').write_text(
        json.dumps(verify(args.check),indent=2)+'\n',encoding='utf-8')
