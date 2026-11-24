#!/usr/bin/env python3
"""Read-only archive verification. Does not execute any archived build scripts."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse, hashlib, json, re, stat, sys, unicodedata, zipfile

ROOT = Path(__file__).resolve().parent
def digest(data):
    return hashlib.sha256(data).hexdigest()
def safe_name(name):
    normalized = name.replace("\\", "/")
    path = PurePosixPath(normalized)
    if path.is_absolute() or ".." in path.parts or re.match(r"^[A-Za-z]:", normalized):
        raise ValueError("Unsafe archive path: " + name)
    return unicodedata.normalize("NFC", normalized)
def check(condition, message):
    if not condition:
        raise ValueError(message)
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", help="Optional JSON report path; only this output is written")
    args = parser.parse_args()
    index_path = ROOT / "INDEX.json"
    index_bytes = index_path.read_bytes()
    index = json.loads(index_bytes)
    totals = {"archives": 0, "members": 0, "internal_sha256_records": 0,
              "zip_bytes": 0, "uncompressed_bytes": 0}
    checked = []
    for rec in index["records"]:
        archive = ROOT / rec["archive_path"]
        raw = archive.read_bytes()
        check(digest(raw) == rec["zip_sha256"], rec["id"] + ": ZIP hash mismatch")
        check(len(raw) == rec["zip_bytes"], rec["id"] + ": ZIP length mismatch")
        folder = ROOT / rec["extracted_directory"]
        expected = {m["path"]: m for m in rec["members"]}
        expected_file_names = {n for n, m in expected.items() if not m["is_directory"]}
        actual_files = {str(p.relative_to(folder)) for p in folder.rglob("*") if p.is_file()}
        check(actual_files == expected_file_names, rec["id"] + ": extraction member set mismatch")
        manifests = []
        with zipfile.ZipFile(archive) as z:
            check(z.testzip() is None, rec["id"] + ": CRC failure")
            infos = z.infolist()
            check(len(infos) == len(expected), rec["id"] + ": member count mismatch")
            seen = set()
            for info in infos:
                key = safe_name(info.filename)
                check(key not in seen, rec["id"] + ": duplicate normalized member")
                seen.add(key)
                check(not info.flag_bits & 1, rec["id"] + ": encrypted member")
                mode = info.external_attr >> 16
                check(not stat.S_ISLNK(mode), rec["id"] + ": symlink member")
                check(info.filename in expected, rec["id"] + ": unexpected member")
                m = expected[info.filename]
                data = z.read(info)
                check(info.is_dir() == m["is_directory"], rec["id"] + ": type mismatch")
                check(len(data) == m["bytes"], rec["id"] + ": member size mismatch")
                check(digest(data) == m["sha256"], rec["id"] + ": archived member hash mismatch")
                check(f"{info.CRC:08x}" == m["crc32"], rec["id"] + ": member CRC metadata mismatch")
                target = folder.joinpath(*PurePosixPath(info.filename).parts)
                check(not target.is_symlink(), rec["id"] + ": extracted symlink")
                if info.is_dir():
                    check(target.is_dir(), rec["id"] + ": missing extracted directory")
                else:
                    check(target.read_bytes() == data, rec["id"] + ": extracted bytes differ")
                    if PurePosixPath(info.filename).name == "SHA256SUMS.txt":
                        manifests.append((PurePosixPath(info.filename).parent, data))
                totals["members"] += 1
                totals["uncompressed_bytes"] += len(data)
            checksum_count = 0
            for parent, content in manifests:
                for line in content.decode("utf-8-sig").splitlines():
                    if not line.strip():
                        continue
                    match = re.fullmatch(r"([0-9a-fA-F]{64})[ \t]+[* ]?(.+)", line)
                    check(match is not None, rec["id"] + ": unsupported checksum line")
                    hashed_name = str(parent / match.group(2))
                    safe_name(hashed_name)
                    check(hashed_name in expected, rec["id"] + ": checksum target absent")
                    check(digest(z.read(hashed_name)) == match.group(1).lower(),
                          rec["id"] + ": internal checksum mismatch")
                    checksum_count += 1
            check(checksum_count == rec["archive_verification"]["internal_sha256_records"],
                  rec["id"] + ": internal checksum record count mismatch")
            totals["internal_sha256_records"] += checksum_count
        check(digest((ROOT / rec["main_tex_path"]).read_bytes()) == rec["source_tex_sha256"],
              rec["id"] + ": main TeX mismatch")
        check(digest((ROOT / rec["main_pdf"]["path"]).read_bytes()) == rec["main_pdf"]["sha256"],
              rec["id"] + ": main PDF mismatch")
        totals["archives"] += 1
        totals["zip_bytes"] += len(raw)
        checked.append({"id": rec["id"], "zip_sha256": rec["zip_sha256"],
                        "member_count": len(expected), "internal_sha256_records": checksum_count,
                        "passed": True})
    report = {
        "status": "passed",
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "index_sha256": digest(index_bytes),
        "verifier_sha256": digest(Path(__file__).read_bytes()),
        "totals": totals,
        "records": checked,
        "boundary": "Archive bytes, CRC, safe paths, member/extraction identity and internal checksums only. No TeX compilation, mathematical review or PDF visual review."
    }
    if args.report:
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "records"}, ensure_ascii=False, indent=2))
if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("FAILED: " + str(exc), file=sys.stderr)
        sys.exit(1)
