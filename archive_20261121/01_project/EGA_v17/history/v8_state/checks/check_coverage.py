#!/usr/bin/env python3
"""Compare exact original-number macro inventories and retained body hashes."""
from pathlib import Path
from collections import Counter
import re, json, hashlib, sys
r=Path(__file__).resolve().parents[1]
oldpath=Path(sys.argv[1]) if len(sys.argv)>1 else r/'history/v7_before_v8/baseline_single.tex'
if not oldpath.exists():raise SystemExit('Supply the version 7 single-file TeX path.')
old=oldpath.read_text(encoding='utf-8');new=(r/'single.tex').read_text(encoding='utf-8')
e=lambda s:Counter(re.findall(r'\\(?:egapar|egastatement|egap|egas)\{([^{}]+)\}',s))
t=lambda s:Counter(re.findall(r'\\tag\*?\{([^{}]+)\}',s))
a,b=e(old),e(new);c,d=t(old),t(new)
body=json.loads((r/'checks/baseline_body_sha256.json').read_text())
coverage={'entries_old':sum(a.values()),'entries_new':sum(b.values()),'added_entries':dict(b-a),'lost_entries':dict(a-b),'tags_old':sum(c.values()),'tags_new':sum(d.values()),'added_tags':dict(d-c),'lost_tags':dict(c-d),'retained_body_files':len(body),'body_hash_mismatches':[k for k,v in body.items() if hashlib.sha256((r/k).read_bytes()).hexdigest()!=v]}
(r/'checks/coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2))
print(json.dumps(coverage,ensure_ascii=False,indent=2))
assert not coverage['lost_entries'] and not coverage['lost_tags'] and not coverage['body_hash_mismatches']
