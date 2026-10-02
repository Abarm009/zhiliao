"""Verify copied baseline hashes without access to the original workspace."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / "migration-manifest.json").read_text())
    files = manifest["files"]
    failures = []
    seen = set()
    total = 0
    for item in files:
        relative = item["target"]
        path = ROOT / relative
        if relative in seen or path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            failures.append(f"Unsafe or duplicate path: {relative}")
            continue
        seen.add(relative)
        if not path.is_file():
            failures.append(f"Missing: {relative}")
            continue
        content = path.read_bytes()
        total += len(content)
        if len(content) != item["size"] or hashlib.sha256(content).hexdigest() != item["sha256"]:
            failures.append(f"Changed: {relative}")
    if failures:
        print("\n".join(failures))
        return 1
    print(f"Verified {len(files)} baseline files, {total} bytes; original workspace not required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
