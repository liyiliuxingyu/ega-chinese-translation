#!/usr/bin/env python3
"""Inspect actual final XeLaTeX logs and bind them to the resulting PDFs."""
from pathlib import Path
import hashlib
import json
import re
import fitz

ROOT=Path(__file__).resolve().parents[1]
rows=[]
for name in ['main','report','single_build/book_single','single_build/audit_single']:
    log=ROOT/(name+'.log'); pdf=ROOT/(name+'.pdf')
    text=log.read_text(errors='replace')
    fatal=[line for line in text.splitlines() if re.search(
        r'^!|Missing character:|Undefined control sequence|LaTeX Error:|There were undefined references|multiply-defined labels|^Overfull',line)]
    rerun=[line for line in text.splitlines() if re.search(r'Rerun to get|Label\(s\) may have changed',line)]
    diagnostics={
      'overfull':len(re.findall(r'^Overfull',text,re.M)),
      'underfull':len(re.findall(r'^Underfull',text,re.M)),
      'font_warnings':len(re.findall(r'Font Warning:',text)),
      'bookmark_token_warnings':len(re.findall(r'Token not allowed in a PDF string',text)),
      'all_warning_lines':[line for line in text.splitlines() if 'Warning:' in line or line.startswith(('Overfull','Underfull'))]
    }
    with fitz.open(pdf) as d: pages=len(d)
    rows.append({'name':name,'pass':not fatal and not rerun,'fatal_or_overfull_lines':fatal,
      'rerun_lines':rerun,'diagnostics':diagnostics,'pages':pages,
      'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
      'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()})
result={'edition':22,'pass':all(x['pass'] for x in rows),'logs':rows,
        'scope':'Final log and PDF existence diagnostics; nonfatal historical warnings are retained'}
(ROOT/'checks/current_build_log_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
raise SystemExit(0 if result['pass'] else 1)
