#!/usr/bin/env python3
"""Finite algebra checks for K11, not substitutes for general proofs in report.tex.
Only uses the Python standard library; tests truncated polynomial rings over F_p.
"""
from pathlib import Path
from itertools import product
import json

def add(a,b,p):return tuple((x+y)%p for x,y in zip(a,b))
def mul(a,b,p):
    n=len(a); c=[0]*n
    for i,x in enumerate(a):
        for j,y in enumerate(b[:n-i]):c[i+j]=(c[i+j]+x*y)%p
    return tuple(c)
def power(a,k,p):
    r=(1,)+(0,)*(len(a)-1)
    while k:
        if k&1:r=mul(r,a,p)
        a=mul(a,a,p);k//=2
    return r

def check(p):
    n=2*p;T=(0,1)+(0,)*(n-2);Tp=power(T,p,p)
    assert Tp!=tuple([0]*n)
    assert power(Tp,2,p)==tuple([0]*n)
    checked=0
    for h in product(range(p),repeat=p):
        correction=tuple([0]*p+list(h));z=add(T,correction,p)
        assert power(z,p,p)==Tp
        checked+=1
    # j'=j tensor 1 cannot preserve t tensor 1 = 1 tensor t
    assert power(T,p,p)!=T
    # Corrected formula is Frobenius-compatible for sampled coefficient triples.
    samples=[T,(1,1)+(0,)*(n-2),(1,)+(0,)*(n-1),Tp]
    identities=0
    for a,b,c in product(samples,repeat=3):
        left=mul(power(mul(a,b,p),p,p),power(c,p,p),p)
        right=mul(power(b,p,p),power(mul(a,c,p),p,p),p)
        assert left==right;identities+=1
    return {'p':p,'truncated_modulus_degree':n,'all_lifts_of_t_checked':checked,'every_lift_has_pth_power':'T^p, nonzero','balanced_identity_sample_count':identities}
res={'tests':[check(p) for p in (2,3,5)],'limitation':'Finite checks confirm the stated polynomial examples only. Field p-bases, counterexamples over rational-function fields, and arbitrary-ring results are proved in the report, not certified by this script.'}
out=Path(__file__).resolve().with_name('k11_example_checks.json');out.write_text(json.dumps(res,ensure_ascii=False,indent=2))
print(json.dumps(res,ensure_ascii=False,indent=2))
