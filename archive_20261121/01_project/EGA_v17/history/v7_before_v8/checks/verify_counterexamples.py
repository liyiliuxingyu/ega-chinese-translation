"""Small symbolic checks only; proofs and scope are in the audit, not replaced here."""
from pathlib import Path
import json
import sympy as s
x,y,t=s.symbols('x y t')
z=y-x**2
image=s.expand(z.subs({x:t,y:t**2}, simultaneous=True))
graded=s.expand(z.subs({x:t,y:0}, simultaneous=True))
assert image==0 and graded==-t**2
# All defining cubic monomials vanish modulo t^3.
cubics=[x**3,x**2*y,x*y**2,y**3]
assert all(s.rem(s.expand(m.subs({x:t,y:t**2},simultaneous=True)),t**3,t)==0 for m in cubics)
assert s.rem(graded,t**3,t)!=0
out={'G7-G01':{'h(y-x^2)':str(image),'gr_h(y-x^2)':str(graded),'nonzero_mod_t3':True},'scope':'Symbolic check of a proof-step counterexample only; not formal verification of the EGA lemma or the whole translation.'}
Path(__file__).with_name('counterexample_check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False,indent=2))
