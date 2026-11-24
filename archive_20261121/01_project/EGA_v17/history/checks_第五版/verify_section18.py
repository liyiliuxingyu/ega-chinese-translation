#!/usr/bin/env python3
"""Finite/symbolic checks for §18 notes, not proofs of all general cases."""
from __future__ import annotations
import itertools, json
from collections import Counter
from pathlib import Path
import sympy as sp
out: dict[str, object] = {}
t = sp.Symbol('t')
p, q, r = t**3 + 2*t + 1, t**2 - 3*t, t**4 + 1
sigma = lambda f: sp.expand(f.subs(t, t+1))
assert sp.expand((p*q)*sigma(r) - p*(q*sigma(r))) == 0
assert sp.expand((p*sigma(q))*sigma(r)-p*sigma(q*r)) == 0
assert sp.expand(t-(t+1)) == -1
out['twisted_bimodule'] = {'mixed_action_difference': 0, 't_left_minus_t_right_on_1': -1}
g = lambda f: sp.diff(f,t,2)
delta = lambda x,y: sp.expand(x*g(y)-g(x*y)+g(x)*y)
assert sp.expand(delta(p,q)+2*sp.diff(p,t)*sp.diff(q,t)) == 0
assert sp.expand(delta(p*q,r)+delta(p,q)*r-p*delta(q,r)-delta(p,q*r)) == 0
assert delta(sp.Integer(1),sp.Integer(1)) == 0 and delta(t,t) == -2
out['hochschild_coboundary'] = {'cocycle_identity_difference': 0, 'delta_g_1_1': 0, 'delta_g_t_t': -2}
def boundary(tensor: tuple[int, ...]) -> Counter:
    n=len(tensor)-1
    ans=Counter()
    if n<1: return ans
    for i in range(n):
        ans[tensor[:i]+(tensor[i]+tensor[i+1],)+tensor[i+2:]] += (-1)**i
    ans[(tensor[-1]+tensor[0],)+tensor[1:-1]] += (-1)**n
    return Counter({k:v for k,v in ans.items() if v})
tests=0
for n in range(2,7):
    for mon in itertools.product(range(3), repeat=n+1):
        ans=Counter()
        for v,c in boundary(mon).items():
            for w,d in boundary(v).items(): ans[w] += c*d
        assert all(c==0 for c in ans.values()), (n,mon,ans)
        tests+=1
for x,y,z in itertools.product(range(4),repeat=3):
    a,b=boundary((x,y,z)),boundary((x,z,y))
    assert all(a[k]==b[k] for k in set(a)|set(b))
out['hochschild_d_squared']={'rings_tested':'Q[t], monomial tensors','n':list(range(2,7)),'cases':tests,'symmetric_extra_d3_cases':64,'all_passed':True}
G=[(x,y) for x in range(9) for y in range(9) if (x-y)%3==0]
K=[0,3,6]
add=lambda a,b:((a[0]+b[0])%9,(a[1]+b[1])%9)
mul=lambda a,b:((a[0]*b[0])%9,(a[1]*b[1])%9)
N=[(0,k) for k in K]
for z in G:
    for k in K:
        assert mul(z,(0,k))==(0,z[1]*k%9)
        assert mul((0,k),z)==(0,k*z[1]%9)
cosets={frozenset(add(z,n) for n in N) for z in G}
assert len(cosets)==9
for coset in cosets: assert len({z[0] for z in coset})==1
reconstructed=[(x,y) for x in range(9) for y in range(9) if x%3==y%3]
u=lambda z:(z[0],z[1])
assert set(map(u,G))==set(reconstructed) and len(set(map(u,G)))==len(G)
for a,b in itertools.product(G,repeat=2):
    assert u(add(a,b))==add(u(a),u(b))
    assert u(mul(a,b))==mul(u(a),u(b))
out['finite_fibre_product']={'G_size':len(G),'kernel_size':len(N),'quotient_size':len(cosets),'reconstructed_size':len(reconstructed),'ring_pair_tests':len(G)**2,'all_passed':True}
out['limitation']='Finite/symbolic computations check displayed examples and formulas only; general arguments remain in the report.'
Path(__file__).with_name('section18_verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False,indent=2))
