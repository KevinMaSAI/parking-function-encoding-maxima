# SPDX-License-Identifier: MIT
"""Run the released checks without rewriting the frozen audit files."""
from pathlib import Path
import argparse,contextlib,io,json,os,sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(HERE))
os.chdir(ROOT)
import exact_counts
import rotation_injection
import eliminate_ties
import odd_prefix_repairs
import binary_maximum_injection
import verify_full_solution
import solve_maximum


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json',type=Path)
    args=parser.parse_args()
    results={}
    stages=[
        ('three_exact_count_methods',lambda:exact_counts.self_check(6)),
        ('odd_alternating_rotation',rotation_injection.verify),
        ('tie_elimination',eliminate_ties.verify),
        ('odd_threshold_map',odd_prefix_repairs.verify),
        ('strict_binary_repairs',lambda:binary_maximum_injection.verify(6)),
        ('full_composed_injection',lambda:verify_full_solution.verify(6)),
    ]
    for name,check in stages:
        with contextlib.redirect_stdout(io.StringIO()):
            data=check()
        results[name]={'passed':True}
        if name=='full_composed_injection':
            results[name]['parking_inputs']=sum(x['all_parking_functions_checked'] for x in data)
        print('PASS',name,flush=True)
    for n in range(1,11):
        row=solve_maximum.solve(n)
        counts=json.loads((HERE/f'counts_n{n}.json').read_text())
        best=max(counts.values())
        observed=sorted(w for w,c in counts.items() if c==best)
        assert row['maximum']==best and sorted(row['maximizers'])==observed
        assert sum(counts.values())==(n+1)**(n-1)
        assert len(counts)==3**(n-1)
    results['complete_ternary_classification']={'passed':True,'through_n':10}
    print('PASS complete_ternary_classification_through_n10',flush=True)
    maximum_rows=json.loads((ROOT/'validation'/'maximum_values_dp_n20.json').read_text())
    for row in maximum_rows:
        observed=solve_maximum.solve(row['n'])
        assert observed['maximum']==row['maximum']
    results['maximum_recurrence']={'passed':True,'through_n':20}
    print('PASS maximum_recurrence_through_n20',flush=True)
    summary={'all_checks_passed':True,'checks':results}
    if args.json:
        args.json.parent.mkdir(parents=True,exist_ok=True)
        with args.json.open('w',encoding='utf-8',newline='\n') as f:
            json.dump(summary,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(summary),flush=True)


if __name__=='__main__':
    main()
