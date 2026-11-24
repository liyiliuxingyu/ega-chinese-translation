#!/usr/bin/env python3
"""Refresh file hashes only. This does NOT validate mathematics or translation."""
import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from package_common import PackageError, refresh_tree


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent,
                        help="package root; defaults to this script's directory")
    parser.add_argument("--json", action="store_true", help="print a machine-readable result")
    args = parser.parse_args()
    try:
        result = refresh_tree(args.root)
    except (PackageError, OSError) as exc:
        print(f"Manifest refresh failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Refreshed MANIFEST.json and SHA256SUMS.txt for {result['payload_files']} payload files.")
        print("This records current bytes; it does NOT validate mathematics, translation, or compilation.")
        print("Run verify_package.py --strict after finalizing the package.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
