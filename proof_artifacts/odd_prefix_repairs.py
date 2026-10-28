# SPDX-License-Identifier: MIT
"""Proved odd-length prefix repairs, including an upper-threshold injection."""
from collections import defaultdict
from itertools import product
from pathlib import Path
import json
from exact_counts import encoding
from rotation_injection import peak_to_valley, inverse_on_image, is_parking


def valley_to_peak_above(a, threshold):
    a=tuple(a)
    k=len(a)
    assert threshold>=1 and k>=3 and k%2==1
    assert encoding(a)=='AD'*(k//2) and a[-1]>threshold
    if a[0]<a[-1]:
        return a[-1:]+a[:-1]
    if a[0]>a[-1]:
        return a[1:]+a[:1]
    return a[1:-1]+(threshold,a[-1])


def inverse_threshold_image(b, threshold):
    b=tuple(b)
    assert b[0]!=b[-1]
    rotated=peak_to_valley(b)
    if rotated[-1]>threshold:
        return rotated
    assert rotated[-1]==threshold and b[-2]==threshold
    return b[-1:]+b[:-2]+b[-1:]


def prefix_plan(w):
    assert 'T' not in w
    i=next((j for j in range(len(w)-1) if w[j]==w[j+1]),None)
    if i is None or (i+2)%2==0:
        return None
    k=i+2
    target=''.join('D' if x=='A' else 'A' for x in w[:k-1])+w[k-1:]
    return {'length':k,'direction':w[i],'target':target}


def forward_prefix(a,plan):
    a=tuple(a)
    k=plan['length']
    if plan['direction']=='A':
        prefix=peak_to_valley(a[:k])
    else:
        prefix=valley_to_peak_above(a[:k],a[k])
    return prefix+a[k:]


def inverse_prefix(b,plan):
    b=tuple(b)
    k=plan['length']
    if plan['direction']=='A':
        prefix=inverse_on_image(b[:k])
    else:
        prefix=inverse_threshold_image(b[:k],b[k])
    return prefix+b[k:]


def verify():
    threshold_records=[]
    for k in range(3,10,2):
        checked=0
        images=defaultdict(set)
        for a in product(range(1,5),repeat=k):
            if encoding(a)!='AD'*(k//2):continue
            for t in range(1,4):
                if a[-1]<=t:continue
                b=valley_to_peak_above(a,t)
                assert encoding(b)=='DA'*(k//2),(a,t,b)
                assert b[-1]>=a[-1]>t
                assert all(x<=y for x,y in zip(sorted(b),sorted(a)))
                assert inverse_threshold_image(b,t)==a,(a,t,b)
                assert b not in images[t]
                images[t].add(b);checked+=1
        record={'odd_length':k,'alphabet':4,'thresholds':[1,2,3],
                'instances_checked':checked,'inverse_and_dominance_verified':True}
        threshold_records.append(record);print(json.dumps(record),flush=True)
    prefix_records=[]
    for n in range(3,7):
        checked=0;images=defaultdict(set)
        for a in product(range(1,n+1),repeat=n):
            w=encoding(a)
            if 'T' in w or not is_parking(a):continue
            plan=prefix_plan(w)
            if plan is None:continue
            b=forward_prefix(a,plan)
            assert encoding(b)==plan['target'],(a,b,plan)
            assert is_parking(b),(a,b,plan)
            assert inverse_prefix(b,plan)==a,(a,b,plan)
            assert b not in images[w]
            images[w].add(b);checked+=1
        r={'n':n,'parking_inputs_checked':checked,
           'per_class_injection_verified':True}
        prefix_records.append(r);print(json.dumps(r),flush=True)
    count_records=[]
    for n in range(3,11):
        counts=json.loads(Path(f'proof_artifacts/counts_n{n}.json').read_text())
        number=0
        for w,v in counts.items():
            if 'T' in w:continue
            p=prefix_plan(w)
            if p is None:continue
            assert counts[p['target']]>v,(n,w,p['target'],v,counts[p['target']])
            number+=1
        count_records.append({'n':n,'strict_prefix_inequalities_checked':number})
    return {'threshold_word_checks':threshold_records,
            'parking_prefix_checks':prefix_records,
            'complete_class_count_checks':count_records}


if __name__=='__main__':
    Path('proof_artifacts/odd_prefix_repairs_audit.json').write_text(
        json.dumps(verify(),indent=2)+'\n',encoding='utf-8')
