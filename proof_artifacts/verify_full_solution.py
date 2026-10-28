# SPDX-License-Identifier: MIT
"""End-to-end check of the composed injection, including reverse recovery."""
from collections import Counter,defaultdict
from itertools import product
from pathlib import Path
import argparse,json
from exact_counts import encoding,brute_counts
from rotation_injection import is_parking,peak_to_valley,inverse_on_image
from eliminate_ties import eliminate_encoding,forward_step as ft,inverse_step as it
from binary_maximum_injection import binary_plan,forward_step as fb,inverse_step as ib
from solve_maximum import solve


def verify(max_n):
    rows=[]
    for n in range(1,max_n+1):
        images=defaultdict(set);counts=Counter();checked=0
        expected=solve(n)
        for a in product(range(1,n+1),repeat=n):
            if not is_parking(a):continue
            checked+=1
            source=encoding(a);counts[source]+=1
            no_t,ties=eliminate_encoding(source)
            b=tuple(a)
            for p in ties:b=ft(b,p)
            alt,binary=binary_plan(no_t)
            for p in binary:b=fb(b,p)
            rotated=n>=3 and n%2==1 and alt.startswith('D')
            if rotated:b=peak_to_valley(b)
            target=encoding(b)
            assert target in expected['maximizers'],(n,a,b,target,expected)
            assert is_parking(b)
            assert b not in images[source],(n,a,b,source)
            images[source].add(b)
            recovered=inverse_on_image(b) if rotated else b
            for p in reversed(binary):recovered=ib(recovered,p)
            for p in reversed(ties):recovered=it(recovered,p)
            assert recovered==a,(a,b,recovered)
        assert checked==(n+1)**(n-1)
        assert max(counts.values())==expected['maximum']
        observed=sorted(w for w,v in counts.items() if v==expected['maximum'])
        assert observed==sorted(expected['maximizers'])
        row={'n':n,'all_parking_functions_checked':checked,
             'source_encoding_classes_checked':len(counts),
             'full_composition_injective_per_class':True,
             'every_original_recovered':True,
             'classification_matches_direct_enumeration':True}
        print(json.dumps(row),flush=True);rows.append(row)
    return rows


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',type=int,default=6)
    args=parser.parse_args()
    Path('proof_artifacts/full_solution_composition_audit.json').write_text(
        json.dumps(verify(args.check),indent=2)+'\n',encoding='utf-8')
