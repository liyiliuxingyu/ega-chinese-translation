from sympy import symbols, Matrix, expand, groebner
x0,x1,x2,x3=symbols("x0:4")
X=Matrix([x0,x1,x2,x3])
Q=x0*x3-x1*x2
G=Matrix([Q.diff(x) for x in X])
assert abs(G.jacobian(X).det())==1
assert expand(Q.subs(dict(zip(X,G)),simultaneous=True))==Q
assert Q.subs(x3,0)==-x1*x2
for d in range(3,8):
    x=symbols(f"x1:{d+1}")
    z=symbols("z")
    B=groebner([z*t for t in (*x,z)],*x,z)
    assert B.reduce(z)[1]==z
    assert all(B.reduce(z*t)[1]==0 for t in (*x,z))
print("Quadratic dual and tangent section; embedded socle, d=3..7: finite symbolic checks passed")
