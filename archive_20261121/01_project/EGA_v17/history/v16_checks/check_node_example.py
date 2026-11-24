"""Symbolic identities in P16-E01; NOT a formal proof of normalization."""
from pathlib import Path
import json
import sympy as s
t=s.symbols('t');x=t*t-1;y=t*(t*t-1)
rel=s.expand(y*y-x*x*(x+1));g=s.gcd(x,y);gpm=s.gcd(t-1,t+1)
assert rel==0 and g==t*t-1 and gpm==1
result={'coefficient_field':'Q','relation_y2_x2_xplus1':str(rel),'gcd_x_y':str(g),'gcd_tminus1_tplus1':str(gpm),'residue_points':[1,-1],'limitation':'Only polynomial identities were executed. Noetherianity, normalization and semilocality are proved in the written report, not certified by this script.'}
Path(__file__).with_name('node_example_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
