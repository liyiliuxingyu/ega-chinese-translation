from pathlib import Path
import hashlib
root = Path(__file__).resolve().parent
for line in (root / "SHA256SUMS.txt").read_text().splitlines():
    sha, name = line.split("  ", 1)
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == sha, name
print("All hashes verified")
