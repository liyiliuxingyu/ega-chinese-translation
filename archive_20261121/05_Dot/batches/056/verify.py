from pathlib import Path
import hashlib
p=Path(__file__).resolve().parent
for line in (p/"SHA256SUMS.txt").read_text().splitlines():
 h,n=line.split("  ",1)
 assert hashlib.sha256((p/n).read_bytes()).hexdigest()==h,n
print("All hashes verified")
