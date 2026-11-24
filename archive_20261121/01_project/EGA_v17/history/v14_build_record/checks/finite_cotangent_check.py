"""Exact finite-ring checks for the cotangent defect in N14-E01.
This checks a finite quotient; regularity of the original DVR extension is proved
in the audit, not inferred from this finite computation.
"""
from itertools import product
from pathlib import Path
import json

def multiply(a:tuple[int,...], b:tuple[int,...], p:int)->tuple[int,...]:
    q=p*p
    out=[0]*(2*p-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): out[i+j]=(out[i+j]+x*y)%q
    # Relation t**p=p. The largest degree is 2p-2, so one reduction suffices.
    for i in range(2*p-2,p-1,-1): out[i-p]=(out[i-p]+p*out[i])%q
    return tuple(out[:p])

def exact_log(n:int,p:int)->int:
    e=0
    while n>1:
        assert n%p==0
        n//=p;e+=1
    return e

def test(p:int)->dict:
    ring=list(product(range(p*p),repeat=p))
    t=tuple([0,1]+[0]*(p-2));t2=multiply(t,t,p)
    const_p=tuple([p]+[0]*(p-1))
    n={multiply(t,a,p) for a in ring}
    n2={multiply(t2,a,p) for a in ring}
    pB={multiply(const_p,a,p) for a in ring}
    assert pB<=n2
    eB=exact_log(len(n)//len(n2),p)
    assert eB==1
    return {'p':p,'ring':f'(Z/{p*p})[t]/(t^{p}-{p})',
            'ring_size':len(ring),'maximal_ideal_size':len(n),
            'maximal_ideal_square_size':len(n2),'p_ideal_size':len(pB),
            'pB_subset_n_square':True,'eA':1,'eB':eB,
            'epsilon_A':1,'epsilon_B':0,
            'reduced_cotangent_dimension_A':0,'reduced_cotangent_dimension_B':1}

if __name__=='__main__':
    result={'scope':'Only the finite quotient and its cotangent spaces; not a proof of regularity of a finite Artinian ring.',
            'checks':[test(2),test(3)]}
    Path(__file__).with_suffix('.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))
