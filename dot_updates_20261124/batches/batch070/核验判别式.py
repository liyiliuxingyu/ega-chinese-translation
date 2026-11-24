#!/usr/bin/env python3
"""Examples with exact integer arithmetic; not a replacement for the general proof."""
from itertools import product,permutations
from math import prod

def det(M):
    n=len(M)
    return sum((-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n)) * prod(M[i][p[i]] for i in range(n)) for p in permutations(range(n)))

def corrected(M):
    h=det(M)
    if len(M)%2:
        assert h%2==0
        h//=2
    return h

def diag(M,N):
    return [row+[0]*len(N) for row in M] + [[0]*len(M)+row for row in N]

for a,b,c,d,e,f in product(range(-1,2),repeat=6):
    B=[[2*a,d,e],[d,2*b,f],[e,f,2*c]]
    h=corrected(B)
    assert h==4*a*b*c-a*f*f-b*e*e-c*d*d+d*e*f
    assert h%2==(a*f*f+b*e*e+c*d*d+d*e*f)%2
    assert corrected(diag(B,[[2]]))==4*h
    assert corrected(diag(B,[[0,1],[1,0]]))==-h
for m in range(4):
    B=[]
    for _ in range(m):
        B=diag(B,[[0,1],[1,0]])
    assert det(B)==(-1)**m
    assert det(diag(B,[[2]]))==2*(-1)**m
print('729 ternary integer cases, 1458 direct-sum comparisons and 8 standard determinants passed.')
