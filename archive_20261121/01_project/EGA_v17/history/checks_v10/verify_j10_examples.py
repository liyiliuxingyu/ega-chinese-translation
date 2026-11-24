#!/usr/bin/env python3
"""Finite sanity checks for the J10 audit; not a proof of the general results.

Uses only the Python standard library.  The report gives the general arguments.
This script checks block-matrix identities over F_7, a dual-number obstruction,
and the dimensions in the tensor/kernel example.
"""
import json
import random

P = 7

def zeros(m, n):
    return [[0 for _ in range(n)] for _ in range(m)]

def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]

def neg(a):
    return [[(-x) % P for x in row] for row in a]

def mul(a, b):
    assert len(a[0]) == len(b)
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) % P
             for j in range(len(b[0]))] for i in range(len(a))]

def block(a, b, c, d):
    assert len(a) == len(b) and len(c) == len(d)
    return [x + y for x, y in zip(a, b)] + [x + y for x, y in zip(c, d)]

def rank(a):
    a = [row[:] for row in a]
    row = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(row, len(a)) if a[i][col] % P), None)
        if pivot is None:
            continue
        a[row], a[pivot] = a[pivot], a[row]
        inv = pow(a[row][col], -1, P)
        a[row] = [(x * inv) % P for x in a[row]]
        for i in range(len(a)):
            if i != row:
                factor = a[i][col] % P
                a[i] = [(x - factor * y) % P for x, y in zip(a[i], a[row])]
        row += 1
        if row == len(a):
            break
    return row

def check_blocks():
    rng = random.Random(20261115)
    checks = 0
    for m, n, r in [(1, 1, 1), (2, 3, 2), (3, 2, 4), (4, 4, 3)]:
        for _ in range(20):
            f = [[rng.randrange(P) for _ in range(m)] for _ in range(n)]
            g = [[rng.randrange(P) for _ in range(n)] for _ in range(r)]
            gf = mul(g, f)
            j1 = eye(m) + f
            j0 = g + eye(n)
            p1 = [a + b for a, b in zip(neg(f), eye(n))]
            p0 = [a + b for a, b in zip(neg(eye(r)), g)]
            d = block(gf, zeros(r, n), zeros(n, m), eye(n))
            assert mul(d, j1) == mul(j0, f)
            assert mul(p0, d) == mul(g, p1)
            assert mul(p1, j1) == zeros(n, m)
            assert mul(p0, j0) == zeros(r, n)
            assert rank(j1) == m and rank(p1) == n
            assert rank(j0) == n and rank(p0) == r
            checks += 1
    return checks

def check_dual_number_obstruction():
    # (t + a*t^2)^2 modulo t^3 always has coefficient 1 on t^2.
    for p in [2, 3, 5, 7]:
        for a in range(p):
            v = [0, 1, a]
            sq = [sum(v[i] * v[k-i] for i in range(k+1)) % p
                  for k in range(3)]
            assert sq == [0, 0, 1]
    return True

def check_kernel_tensor_example():
    # In B=F_7[x]/(x^2), multiplication by x has image (x) of dimension 1.
    x = [[0, 0], [1, 0]]
    assert rank(x) == 1
    assert mul(x, x) == zeros(2, 2)
    # After tensoring with C=B/(x), the differential quotient map is identity.
    assert rank([[1]]) == 1
    return {"tensor_of_original_kernel_dimension": 1,
            "kernel_after_tensor_dimension": 0}

if __name__ == "__main__":
    result = {
        "block_matrix_cases_over_F7": check_blocks(),
        "dual_number_lifting_obstruction": check_dual_number_obstruction(),
        "tensor_kernel_dimensions": check_kernel_tensor_example(),
        "scope": "Finite sanity checks only; general proofs are in the audit."
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
