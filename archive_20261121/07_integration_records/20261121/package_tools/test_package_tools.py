#!/usr/bin/env python3
"""Small synthetic integrity/restoration tests; does not alter the real package."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
from package_common import (MANIFEST, RESTORE_INDEX, SUMS, PackageError,
                            refresh_tree, relative_parts, verify_tree)
from restore_versions import restore

TOOLS = Path(__file__).resolve().parent


class PackageToolsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="ega-package-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "package"
        self.root.mkdir()
        self.current = "01_project/EGA_v17/正文.tex"
        self.current_bytes = "\\documentclass{ctexbook}\n正文：α与中文。\n".encode()
        self.old_bytes = b"historical bytes\x00\xff\n"
        self.old_hash = hashlib.sha256(self.old_bytes).hexdigest()
        self.stored = f"04_history/content/{self.old_hash[:2]}/{self.old_hash}"
        self.put(self.current, self.current_bytes)
        self.put(self.stored, self.old_bytes)
        original = {"original_path": "原目录/旧稿.bin", "stored_path": self.stored,
                    "bytes": len(self.old_bytes), "sha256": self.old_hash}
        current = {"original_path": "project/main.tex", "stored_path": self.current,
                   "bytes": len(self.current_bytes),
                   "sha256": hashlib.sha256(self.current_bytes).hexdigest()}
        archive = {"file_name": "original.zip", "bytes": 42, "sha256": "a" * 64}
        self.index = {"schema_version": 1, "versions": {
            "v17": {"root_name": "EGA_v17_handover", "archive": archive,
                    "files": [original, current]},
            "supplement_III": {"root_name": "EGA_v17_V_supplement_III",
                               "archive": archive, "files": [current]},
            "supplement_III_delta": {"root_name": "EGA_v17_V_supplement_III_delta",
                                     "archive": archive, "files": [original]}}}
        self.save_index()

    def put(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def save_index(self):
        self.put(RESTORE_INDEX, (json.dumps(self.index, ensure_ascii=False) + "\n").encode())
        refresh_tree(self.root)

    def cli(self, script, *args):
        return subprocess.run([sys.executable, "-B", str(TOOLS / script),
                               "--root", str(self.root), *map(str, args)],
                              text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def replace_manifest_and_rehash_it(self, document):
        data = (json.dumps(document, ensure_ascii=False) + "\n").encode()
        self.put(MANIFEST, data)
        lines = (self.root / SUMS).read_text().splitlines()
        lines = [hashlib.sha256(data).hexdigest() + "  " + MANIFEST
                 if line.endswith("  " + MANIFEST) else line for line in lines]
        self.put(SUMS, ("\n".join(lines) + "\n").encode())

    def test_valid_strict_and_cli(self):
        result, records = verify_tree(self.root, strict=True)
        self.assertTrue(result["pass"])
        self.assertEqual(len(records), 3)
        completed = self.cli("verify_package.py", "--strict", "--json")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(json.loads(completed.stdout)["pass"])
        self.assertFalse((self.root / "__pycache__").exists())

    def test_refresh_cli(self):
        self.put("03_sources/new.bin", b"new source")
        completed = self.cli("refresh_manifest.py", "--json")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["payload_files"], 4)
        verify_tree(self.root, strict=True)

    def test_tampered_payload(self):
        self.put(self.current, b"changed")
        with self.assertRaises(PackageError):
            verify_tree(self.root)

    def test_manifest_hash_is_checked(self):
        self.put(MANIFEST, (self.root / MANIFEST).read_bytes() + b" ")
        with self.assertRaisesRegex(PackageError, "MANIFEST.json SHA-256"):
            verify_tree(self.root)

    def test_missing_payload(self):
        (self.root / self.current).unlink()
        with self.assertRaises(PackageError):
            verify_tree(self.root)

    def test_extra_files_only_fail_strict(self):
        self.put("extra.txt", b"extra")
        result, _ = verify_tree(self.root)
        self.assertEqual(result["extra_files"], ["extra.txt"])
        with self.assertRaises(PackageError):
            verify_tree(self.root, strict=True)

    def test_unsafe_path_components(self):
        for name in ("../outside", "/absolute", "a/../b", "a//b", "a/./b", "",
                     "a\\b", "C:relative", "folder/file:stream", "x\ny", ".", ".."):
            with self.subTest(path=name), self.assertRaises(PackageError):
                relative_parts(name)

    def test_cross_platform_path_aliases_are_rejected(self):
        for name in ("a/.. /escape", "a./b", "name ", "NUL", "con.txt", "COM1.log",
                     "folder/LPT²", "a?b", "a*b", "a\u2028b", "a\x85b"):
            with self.subTest(path=name), self.assertRaises(PackageError):
                relative_parts(name)

    def test_unsafe_manifest_path(self):
        document = json.loads((self.root / MANIFEST).read_text())
        document["files"][0]["path"] = "../outside"
        self.replace_manifest_and_rehash_it(document)
        with self.assertRaises(PackageError):
            verify_tree(self.root)

    def test_duplicate_manifest_path(self):
        document = json.loads((self.root / MANIFEST).read_text())
        document["files"].append(document["files"][0])
        self.replace_manifest_and_rehash_it(document)
        with self.assertRaisesRegex(PackageError, "Duplicate manifest"):
            verify_tree(self.root)

    def test_duplicate_checksum_path(self):
        lines = (self.root / SUMS).read_bytes()
        self.put(SUMS, lines + lines.splitlines(keepends=True)[0])
        with self.assertRaisesRegex(PackageError, "Duplicate checksum"):
            verify_tree(self.root)

    def test_checksum_sets_must_match(self):
        lines = (self.root / SUMS).read_text().splitlines()
        lines = [line for line in lines if not line.endswith("  " + self.current)]
        self.put(SUMS, ("\n".join(lines) + "\n").encode())
        with self.assertRaisesRegex(PackageError, "path sets differ"):
            verify_tree(self.root)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlink_file_is_rejected_even_when_extra(self):
        outside = self.base / "outside.bin"
        outside.write_bytes(b"outside")
        (self.root / "linked.bin").symlink_to(outside)
        with self.assertRaises(PackageError):
            verify_tree(self.root)
        with self.assertRaises(PackageError):
            refresh_tree(self.root)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlink_directory_is_rejected(self):
        (self.root / "linked-dir").symlink_to(self.base, target_is_directory=True)
        with self.assertRaises(PackageError):
            verify_tree(self.root)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFOs unavailable")
    def test_special_file_is_rejected_without_opening(self):
        os.mkfifo(self.root / "pipe")
        with self.assertRaises(PackageError):
            verify_tree(self.root)

    def test_restore_rehashes_exact_bytes(self):
        destination = self.base / "restored"
        result = restore(self.root, "v17", destination, strict=True)
        recovered = Path(result["restored_root"])
        self.assertEqual((recovered / "原目录/旧稿.bin").read_bytes(), self.old_bytes)
        self.assertEqual((recovered / "project/main.tex").read_bytes(), self.current_bytes)
        self.assertTrue(result["all_restored_files_rehashed"])
        self.assertFalse(result["archive_container_recreated"])

    def test_dynamic_delta_version_and_list_cli(self):
        completed = self.cli("restore_versions.py", "--list", "--json")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("supplement_III_delta", json.loads(completed.stdout)["versions"])
        completed = self.cli("restore_versions.py", "--version", "supplement_III_delta",
                             "--destination", self.base / "delta", "--strict", "--json")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["files"], 1)

    def test_nonempty_destination_is_not_overwritten(self):
        destination = self.base / "nonempty"
        destination.mkdir()
        marker = destination / "keep.txt"
        marker.write_bytes(b"keep")
        with self.assertRaisesRegex(PackageError, "not empty"):
            restore(self.root, "v17", destination)
        self.assertEqual(marker.read_bytes(), b"keep")
        self.assertEqual(list(destination.iterdir()), [marker])

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlink_destination_is_rejected(self):
        actual = self.base / "actual"
        actual.mkdir()
        destination = self.base / "destination-link"
        destination.symlink_to(actual, target_is_directory=True)
        with self.assertRaises(PackageError):
            restore(self.root, "v17", destination)
        self.assertEqual(list(actual.iterdir()), [])

    def test_original_path_traversal_fails_before_creating_destination(self):
        self.index["versions"]["v17"]["files"][0]["original_path"] = "../../escaped.bin"
        self.save_index()
        destination = self.base / "not-created"
        with self.assertRaises(PackageError):
            restore(self.root, "v17", destination)
        self.assertFalse(destination.exists())
        self.assertFalse((self.base / "escaped.bin").exists())

    def test_stored_path_traversal_is_rejected(self):
        self.index["versions"]["v17"]["files"][0]["stored_path"] = "../outside.bin"
        self.save_index()
        with self.assertRaises(PackageError):
            restore(self.root, "v17", self.base / "restored")

    def test_restore_index_mismatch_fails_before_creating_destination(self):
        self.index["versions"]["v17"]["files"][0]["sha256"] = "0" * 64
        self.save_index()
        destination = self.base / "not-created"
        with self.assertRaisesRegex(PackageError, "disagree"):
            restore(self.root, "v17", destination)
        self.assertFalse(destination.exists())

    def test_file_directory_collision_is_rejected(self):
        entries = self.index["versions"]["v17"]["files"]
        entries[0]["original_path"] = "parent"
        entries[1]["original_path"] = "parent/child"
        self.save_index()
        with self.assertRaisesRegex(PackageError, "parent directory"):
            restore(self.root, "v17", self.base / "restored")

    def test_restoration_inside_package_is_rejected(self):
        with self.assertRaisesRegex(PackageError, "outside the package"):
            restore(self.root, "v17", self.root / "restore-output")
        self.assertFalse((self.root / "restore-output").exists())

    def test_duplicate_json_key_is_rejected(self):
        data = (self.root / RESTORE_INDEX).read_text()
        data = data.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1', 1)
        self.put(RESTORE_INDEX, data.encode())
        refresh_tree(self.root)
        with self.assertRaisesRegex(PackageError, "Duplicate JSON"):
            restore(self.root, "v17", self.base / "restored")


if __name__ == "__main__":
    unittest.main(verbosity=2)
