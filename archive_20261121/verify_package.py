#!/usr/bin/env python3
"""Read-only verification of an EGA handover package. Python 3.9+."""
import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from package_common import PackageError, verify_tree


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent,
                        help="package root; defaults to this script's directory")
    parser.add_argument("--strict", action="store_true", help="also reject unlisted ordinary files")
    parser.add_argument("--json", action="store_true", help="print a machine-readable result")
    args = parser.parse_args()
    try:
        result, _ = verify_tree(args.root, strict=args.strict)
    except (PackageError, OSError) as exc:
        if args.json:
            print(json.dumps({"pass": False, "error": str(exc)}, ensure_ascii=False))
        else:
            print(f"Verification failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Verified {result['payload_files']} payload files, "
              f"{result['payload_bytes']} bytes, and the MANIFEST checksum.")
        if result["extra_files"]:
            print(f"Unlisted ordinary files: {len(result['extra_files'])}; use --strict to reject them.")
        print("Scope: file integrity only; no mathematical or translation validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
