#!/usr/bin/env python3
r"""
Tigrinya Skill Synchronization Tool
Synchronizes canonical files from C:\Users\naibm\Documents\projects\english-tigrinya-translator
to both workspace and global Antigravity skill folders:
1. c:\Users\naibm\Documents\projects\tigrinya-catena\.agents\skills\english-tigrinya-translator
2. C:\Users\naibm\.gemini\antigravity\skills\english-tigrinya-translator

Verifies SHA-256 hash parity across all files to guarantee 100% synchronization.
"""

import sys
import os
import shutil
import hashlib
from typing import List, Tuple, Dict

# Ensure stdout handles UTF-8 on all platforms
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CANONICAL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

TARGET_DIRS = [
    r"c:\Users\naibm\Documents\projects\tigrinya-catena\.agents\skills\english-tigrinya-translator",
    r"C:\Users\naibm\.gemini\antigravity\skills\english-tigrinya-translator",
]

SYNC_FILES = [
    "SKILL.md",
    "README.md",
    "scripts/audit_translation.py",
    "scripts/studio.py",
    "scripts/sync_skill.py",
    "scripts/test_studio.py",
    "references/anti-amharic.md",
    "references/bibliography-and-sources.md",
    "references/decisions.md",
    "references/examples.md",
    "references/idioms-and-expressions.md",
    "references/orthography.md",
    "references/pronouns.md",
    "references/theological-glossary.md",
    "references/verb-skeleton.md",
]


def compute_sha256(filepath: str) -> str:
    """Compute SHA-256 hexadecimal digest of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def sync_all() -> bool:
    print("==================================================")
    print("  Tigrinya Skill Repository Synchronizer")
    print(f"  Canonical Source: {CANONICAL_DIR}")
    print("==================================================\n")

    # 1. Verify all canonical files exist
    canonical_hashes: Dict[str, str] = {}
    for rel_path in SYNC_FILES:
        src = os.path.join(CANONICAL_DIR, rel_path)
        if not os.path.isfile(src):
            print(f"[ERROR] Canonical file missing: {src}")
            return False
        canonical_hashes[rel_path] = compute_sha256(src)

    all_matched = True

    for target_dir in TARGET_DIRS:
        print(f"Synchronizing to target:\n  {target_dir}")
        os.makedirs(target_dir, exist_ok=True)

        for rel_path in SYNC_FILES:
            src = os.path.join(CANONICAL_DIR, rel_path)
            dest = os.path.join(target_dir, rel_path)
            os.makedirs(os.path.dirname(dest), exist_ok=True)

            shutil.copy2(src, dest)
            dest_hash = compute_sha256(dest)
            expected_hash = canonical_hashes[rel_path]

            if dest_hash != expected_hash:
                print(f"  [FAIL] Hash mismatch on {rel_path}!")
                all_matched = False
            else:
                print(f"  [OK] {rel_path} (hash: {dest_hash[:10]}...)")

        print()

    print("=" * 50)
    if all_matched:
        print(f"SUCCESS: All {len(SYNC_FILES)} files synchronized with 100% hash parity across both targets.")
    else:
        print("FAIL: One or more files failed hash parity verification.")

    return all_matched


def main():
    success = sync_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
