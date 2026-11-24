#!/usr/bin/env python3
"""Exact finite calculations for F6-E01 and F6-G03; not a theorem prover."""
from fractions import Fraction as Q
from pathlib import Path
import json

def mul(a,b,order):
    c=[Q(0)]*order
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            if i+j<order:c[i+j]+=x*y
    return c
one=[Q(1),Q(0)]
unit=[Q(1),Q(1)]
inverse=[Q(1),Q(-1)]
assert mul(unit,inverse,2)==one
h_x=[Q(0),Q(1,2),Q(0)]
h_x2=[Q(0),Q(0),Q(1,2)]
square=mul(h_x,h_x,3)
assert square==[Q(0),Q(0),Q(1,4)]
assert square!=h_x2
result={
 'F6-E01':{'(1+t)(1-t) modulo t^2':[str(x) for x in mul(unit,inverse,2)],'unit_relation_passed':True,
 'non_liftability':'Proved in the report by the classification of units of k[t], not by enumeration.'},
 'F6-G03':{'h(x^2)':[str(x) for x in h_x2],'h(x)^2':[str(x) for x in square],'multiplicativity_fails':True},
 'limitation':'These exact computations check only the displayed identities; the report supplies the mathematical arguments.'}
(Path(__file__).parent/'example_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
