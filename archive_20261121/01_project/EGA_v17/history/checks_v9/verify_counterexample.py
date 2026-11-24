#!/usr/bin/env python3
"""Exhaustively verify the dual-number derivations used in I9-E01.
Elements of F_2[e]/(e^2) are encoded a+2*b, a,b in F_2.
The general proof is in the audit; this checks only the finite example.
"""
import json
from pathlib import Path

def add(x: int, y: int) -> int:
    return x ^ y

def mul(x: int, y: int) -> int:
    a, b = x & 1, x >> 1
    c, d = y & 1, y >> 1
    return (a*c) | (((a*d) ^ (b*c)) << 1)

def deriv(x: int, m: int) -> int:
    return m if x >> 1 else 0

checks = 0
for m in range(4):
    assert deriv(1, m) == 0
    checks += 1
    for x in range(4):
        for y in range(4):
            assert deriv(add(x, y), m) == add(deriv(x, m), deriv(y, m))
            assert deriv(mul(x, y), m) == add(mul(x, deriv(y, m)), mul(y, deriv(x, m)))
            checks += 2
assert deriv(2, 1) == 1
assert mul(2, deriv(2, 1)) == 2 != 0
result = {
    'ring': 'F_2[epsilon]/(epsilon^2)', 'elements': 4,
    'derivations_checked': 4, 'additivity_leibniz_unit_assertions': checks,
    'epsilon_times_D1_epsilon': 'epsilon != 0', 'status': 'passed',
    'limitation': 'Finite example only; not a computer proof of the general statements.'
}
Path(__file__).with_name('counterexample_result.json').write_text(json.dumps(result, indent=2, ensure_ascii=False))
print(json.dumps(result, indent=2, ensure_ascii=False))
