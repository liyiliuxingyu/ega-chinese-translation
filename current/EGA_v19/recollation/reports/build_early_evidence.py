#!/usr/bin/env python3
"""Reproduce the limited preservation and polynomial checks for EGA V 8.14--8.18.

Reads the immutable edition18 inputs and only writes sibling evidence files
and the marked historical-note block of v19_8_14_18_audit.tex.
Does not compile TeX or claim a machine proof of the geometric arguments.
"""
from pathlib import Path
import hashlib
import itertools
import json
import re
import sympy as sp

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
ROOT = WORK.parent
REPO = ROOT / "ega-recovery"
OLD_REL = "current/EGA_v18/continuations/v18_first_8_14_onward.tex"
OLD = REPO / OLD_REL
AUDIT = HERE / "v19_8_14_18_audit.tex"
BODY = WORK / "sections/v19_8_14_18.tex"
START = "% BEGIN D19 HISTORICAL NOTES"
END = "% END D19 HISTORICAL NOTES"
PLACEHOLDER = "% HISTORICAL_NOTES_WILL_BE_APPENDED_BELOW_BY_THE_PRESERVATION_SCRIPT"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def file_record(path):
    b = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "bytes": len(b), "sha256": sha(b)}

def unescaped(text, index):
    count = 0
    while index > 0 and text[index - 1] == "\\":
        index -= 1
        count += 1
    return count % 2 == 0

old = OLD.read_text(encoding="utf-8")
boundary = old.index("% DOT_IMPORT 11 ")
segment = old[:boundary]
notes = []
for match in re.finditer(r"\\(transnote|footnote|ednote)\s*\{", segment):
    begin = match.end()
    depth = 1
    index = begin
    while depth and index < len(segment):
        if unescaped(segment, index):
            if segment[index] == "{":
                depth += 1
            elif segment[index] == "}":
                depth -= 1
        index += 1
    if depth:
        raise ValueError("Unbalanced historical note at " + str(match.start()))
    content = segment[begin:index-1]
    notes.append({
        "number": len(notes)+1,
        "macro": match.group(1),
        "source_start_character_zero_based": match.start(),
        "source_end_character_exclusive": index,
        "source_start_line_one_based": segment.count("\n", 0, match.start())+1,
        "content_sha256": sha(content.encode("utf-8")),
        "content": content,
    })
assert notes
history = [
    START,
    r"\subsec{D19-8.14--8.18：第十八版旧注逐条原样留存}",
    "下列各项按第十八版原文件中的出现顺序保存旧脚注、译注和编者注，注内文字与数学源码逐字保留，仅把脚注容器改为本报告的编号条目。它们是历史记录，不是第十九版新的待核清单：其中关于“相切”、$(R_k)$、8.17(c)的可辨条件、8.18的奇异性、闭包横线及末附记的旧疑读，已经由本轮法文图像核对更新。应以本报告前述校记及正文现行脚注为准。原片段另存本目录的文本档案，可逐字复核正文与注释的旧状态。",
    r"\begin{enumerate}",
]
for note in notes:
    label = {"transnote": "旧译注", "footnote": "旧脚注", "ednote": "旧编者注"}[note["macro"]]
    history.append(r"\item \textbf{" + label + " " + str(note["number"]) + "。}" + note["content"])
history.extend([r"\end{enumerate}", END])
block = "\n".join(history)
audit = AUDIT.read_text(encoding="utf-8")
if PLACEHOLDER in audit:
    assert audit.count(PLACEHOLDER) == 1
    audit = audit.replace(PLACEHOLDER, block)
elif START in audit and END in audit:
    left, remainder = audit.split(START, 1)
    _, right = remainder.split(END, 1)
    audit = left + block + right
else:
    raise ValueError("Historical-note insertion marker not found")
assert PLACEHOLDER not in audit
for note in notes:
    assert note["content"] in audit
AUDIT.write_text(audit, encoding="utf-8")
(HERE / "v19_early_old_segment.tex.txt").write_text(segment, encoding="utf-8")

# Finite polynomial checks for the counterexamples. Geometry remains a written argument.
z, u, w, lam = sp.symbols("z u w lambda")
x = sp.symbols("x1:5")
quadratic = [x[i]*x[j] for i,j in itertools.combinations_with_replacement(range(4),2)]
cubic = [x[i]*x[j]*x[k] for i,j,k in itertools.combinations_with_replacement(range(4),3)]
coordinates = [z**3] + [z*m for m in quadratic] + cubic
pullback = {z:1, x[0]:u, x[1]:lam*u, x[2]:w, x[3]:lam*w}
pulled = [sp.expand(c.subs(pullback)) for c in coordinates]
orders = [min(m[0]+m[1] for m,coefficient in sp.Poly(p,u,w,lam).terms()) for p in pulled[1:]]
vanishing = all(sp.expand(sp.diff(p,v)).subs({u:0,w:0}) == 0 for p in pulled[1:] for v in (u,w,lam))
quadric_zero = sp.expand((x[0]*x[3]-x[1]*x[2]).subs(pullback)) == 0
a,b,c,d,e,f = sp.symbols("a b c d e f")
matrix = sp.Matrix([[a,d,e],[d,b,f],[e,f,c]])
delta = a*b*c+2*d*e*f-a*f**2-b*e**2-c*d**2
det_zero = sp.expand(matrix.det()-delta) == 0
rank_double = sp.diag(1,0,0).rank()
rank_distinct = sp.Matrix([[0,sp.Rational(1,2),0],[sp.Rational(1,2),0,0],[0,0,0]]).rank()
cone_x,cone_y,cone_z=sp.symbols("cone_x cone_y cone_z")
cone = cone_x*cone_z-cone_y**2
cone_double = sp.expand(cone.subs(cone_x,0)) == -cone_y**2
checks = {
    "method": "SymPy finite symbolic identities and monomial enumeration; no claim of a computer-checked geometric proof",
    "sympy_version": sp.__version__,
    "8.16": {
        "coordinate_counts": [1,len(quadratic),len(cubic)],
        "total_coordinate_count": len(coordinates),
        "distinct_formal_coordinates": len(set(coordinates)),
        "ordered_coordinates": [str(q) for q in coordinates],
        "pullback_on_z_equals_s_equals_1": [str(q) for q in pulled],
        "orders_in_u_w_for_last_30": orders,
        "all_last_30_in_I_C_squared": min(orders) >= 2,
        "all_differentials_of_last_30_vanish_on_C": vanishing,
        "quadric_relation_after_pullback_is_zero": quadric_zero,
        "chart_recovery": "On x_i^3 != 0, (x_i^2 x_j)/(x_i^3)=x_j/x_i and (z x_i^2)/(x_i^3)=z/x_i. Geometric closed-immersion and regular-local-ring deductions are written in the TeX audit, not machine proved.",
    },
    "8.18_veronese": {
        "determinant_equals_displayed_delta": det_zero,
        "rank_of_double_line_x_squared": rank_double,
        "rank_of_distinct_lines_xy": rank_distinct,
        "dimension_and_irreducibility_argument": "Written proof in audit; not inferred from the determinant computation alone",
    },
    "8.18_cone": {"x_zero_section_is_minus_y_squared": cone_double},
}
checks["all_finite_checks_passed"] = bool(len(coordinates)==31 and len(set(coordinates))==31 and min(orders)>=2 and vanishing and quadric_zero and det_zero and rank_double==1 and rank_distinct==2 and cone_double)
assert checks["all_finite_checks_passed"]
(HERE / "v19_early_symbolic_checks.json").write_text(json.dumps(checks,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

sources = [REPO/"archive_20261121/03_sources/EGA5_francais.pdf", REPO/"archive_20261121/03_sources/EGAVaiello.pdf", OLD, REPO/"current/EGA_v18/continuations/v18_batch108.tex"]
images = sorted((HERE/"early_source_pages").glob("*.png"))
migration = {
    "task": "Edition19 first essay 8.14--8.18 French/English recollation",
    "source_files": [file_record(p) for p in sources],
    "replacement_boundary": {
        "old_relative_path": OLD_REL,
        "start": "Beginning of file: DOT_IMPORT 08",
        "end_exclusive": "First % DOT_IMPORT 11 line",
        "old_span_utf8_bytes": len(segment.encode("utf-8")),
        "old_span_lines": len(segment.splitlines()),
        "old_span_sha256": sha(segment.encode("utf-8")),
        "old_imports_replaced": [8,9,10],
        "source_french_physical_pages": [46,47,48,49,50],
        "source_english_physical_pages": [32,33,34],
        "first_source_text": "Combinant 8.13, 8.5 et 8.6",
        "last_source_text": "N.B. ending with ne pas exiger d=2, mais seulement d>=2",
        "excluded_next_source_text": "Il reste a expliciter les conditions a) et b) de 8.18",
    },
    "old_notes": notes,
    "old_note_count": len(notes),
    "old_notes_preserved_verbatim_in_audit": True,
    "new_files": [file_record(BODY),file_record(AUDIT),file_record(HERE/"v19_early_old_segment.tex.txt"),file_record(HERE/"v19_early_symbolic_checks.json")],
    "actually_viewed_source_images": [file_record(p) for p in images],
    "image_method": "Full pages rendered with pdftoppm at150dpi; named crops with PyMuPDF at300dpi. All listed images actually viewed; no final-book layout claim.",
    "input_order": ["Existing v18_batch108.tex (8.13)","sections/v19_8_14_18.tex (8.14--8.18)","Sibling v19_8_end.tex (post8.18 linear systems; outside this subtask)"],
    "macro_requirements": "Existing egas, source, transnote, ednote, proof; PD/depth/codim confined to begingroup. Audit uses existing head/subsec/source.",
    "mathematical_scope": [
        "Explicit 8.16 counterexample to codimension-two exceptional non-unramified locus",
        "8.16 sufficient version with global unramifiedness retaining geometric normality, depth>=3 at closed points, geometric integrality, and properness",
        "8.17(a) blow-up counterexample; does not satisfy 8.18 finite exceptional set",
        "8.18 Veronese and normal cone counterexamples to irreducibility-only existence conditions",
        "8.18 sufficient version only: normal X and geometrically integral witnessing sections; no claim of equivalence to original general theorem",
    ],
    "unresolved": [
        "All necessity directions of 8.14 in arbitrary non-equidimensional settings were not re-proved",
        "8.15 missing number beyond right scan edge",
        "Dense overtyping/deleted French layers not fully recoverable",
        "8.17(c) scope of negation in n'est pas gen. fini et inseparable; dependence on incomplete 8.8",
        "8.18 original nonnormal generalization and original final claimed inclusion relation not established",
    ],
    "build_status": "No compilation by this subtask. Parent builds final project and single-file editions.",
    "independent_review": "dot_middle read the actual body/audit and independently checked small-resolution/cubic counterexample and both 8.18 examples; two clarifications requested by root have been incorporated.",
}
(HERE / "v19_early_migration.json").write_text(json.dumps(migration,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"old_notes":len(notes),"old_span_lines":len(segment.splitlines()),"all_finite_checks_passed":checks["all_finite_checks_passed"],"body":file_record(BODY),"audit":file_record(AUDIT)},ensure_ascii=False,indent=2))
