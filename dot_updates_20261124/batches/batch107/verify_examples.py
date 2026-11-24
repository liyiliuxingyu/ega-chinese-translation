from sympy import symbols, diff, groebner, Poly, factor, QQ, S
x,y,z=symbols('x y z')
f=(x*x-z*z)**2+y*z**3+y**4
df=[diff(f,v) for v in (x,y,z)]
for v in (x,y,z):
    u=[i for i in (x,y,z) if i!=v]
    gb=groebner([a.subs(v,1) for a in df],*u,domain=QQ)
    assert gb.contains(S.One)
assert factor(f.subs({y:0,z:1}))==(x-1)**2*(x+1)**2
for i in (-1,1):
    assert df[1].subs({x:i,y:0,z:1})==1
    assert diff(f,x,2).subs({x:i,y:0,z:1})==8
for p in (2,3,5,7,11):
    g=x**(p+1)+y**(p+1)+z**(p+1)
    for v in (x,y,z):
        assert Poly(diff(g,v)-v**p,x,y,z,modulus=p).is_zero
        for u in (x,y,z):
            assert Poly(diff(g,v,u),x,y,z,modulus=p).is_zero
print('PASS: quartic three patches, bitangency and p=2,3,5,7,11 polynomial checks')
