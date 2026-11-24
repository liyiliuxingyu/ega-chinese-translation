#!/usr/bin/env python3
"""Exact checks of selected discriminant examples, not a proof of all of 16.9."""
from pathlib import Path
import json
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
rows = []
for n in range(1, 9):
    matrix = sp.zeros(n)
    for i in range(0, n - 1, 2):
        matrix[i, i + 1] = matrix[i + 1, i] = 1
    if n % 2:
        matrix[n - 1, n - 1] = 2
    discriminant = matrix.det() / (2 if n % 2 else 1)
    expected = (-1) ** (n // 2)
    assert discriminant == expected
    rows.append({"rank": n, "polar_determinant": int(matrix.det()),
                 "corrected_discriminant": int(discriminant),
                 "expected_unit": expected})

a, b, c, d, e, f = sp.symbols("a b c d e f")
polar = sp.Matrix([[2*a, d, e], [d, 2*b, f], [e, f, 2*c]])
ternary = sp.expand(polar.det() / 2)
expected_ternary = 4*a*b*c + d*e*f - a*f**2 - b*e**2 - c*d**2
assert sp.expand(ternary - expected_ternary) == 0
odd_plus_odd = sp.diag(2*a, 2*b).det()
assert sp.expand(odd_plus_odd - 4*a*b) == 0
standard_ternary = ternary.subs({a: 0, b: 0, c: 1, d: 1, e: 0, f: 0})
assert standard_ternary == -1

result = {
    "pass": True,
    "date": "2026-11-25",
    "scope": "Exact integer and symbolic examples under the polar-matrix convention of 16.1 and corrected discriminant of 16.5; not a classification proof or a full audit of 16.9.",
    "source_batches": [69, 70, 71],
    "standard_forms": rows,
    "ternary_form": "a*x^2+b*y^2+c*z^2+d*x*y+e*x*z+f*y*z",
    "ternary_corrected_discriminant": str(ternary),
    "rank_one_plus_rank_one_discriminant": str(odd_plus_odd),
    "standard_ternary_corrected_discriminant": int(standard_ternary),
    "sympy_version": sp.__version__,
}
target = ROOT / "checks/quadratic_examples.json"
target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
