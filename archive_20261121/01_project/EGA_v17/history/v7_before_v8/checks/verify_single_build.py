from pathlib import Path
import subprocess, json, shutil, time
root=Path(__file__).resolve().parents[1]
subprocess.run(['python3','flatten_sources.py'],cwd=root,check=True)
out=root/'single_build';out.mkdir(exist_ok=True)
result={}
for src,name in [('single.tex','book_single'),('report_single.tex','audit_single')]:
 shutil.copy2(root/src,out/(name+'.tex'))
 for ext in ('aux','toc','out'):(out/(name+'.'+ext)).unlink(missing_ok=True)
 for i in range(1,4):
  with (out/f'{name}.pass{i}.log.txt').open('wb') as f:
   cp=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error',name+'.tex'],cwd=out,stdout=f,stderr=subprocess.STDOUT)
  if cp.returncode:
   (root/'checks/single_build_status.json').write_text(json.dumps({'failed':name,'pass':i,'returncode':cp.returncode})); raise SystemExit(cp.returncode)
 result[name]={'passes':3,'returncode':0}
(root/'checks/single_build_status.json').write_text(json.dumps(result,indent=2))
