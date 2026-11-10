"""Write, or check, a SHA-256 manifest of every file under results/.

The answer files are gitignored (789 MB), so git cannot archive them. The
manifest records each file's size and hash, so a later run can prove it left
every existing result untouched.

  py -3.14 scripts/results_manifest.py write manifests/results-manifest.tsv
  py -3.14 scripts/results_manifest.py check manifests/results-manifest.tsv
"""

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main():
    mode, target = sys.argv[1], ROOT / sys.argv[2]
    if mode == "write":
        rows = []
        for p in sorted(RESULTS.rglob("*")):
            if p.is_file():
                rows.append(f"{p.relative_to(ROOT).as_posix()}\t{p.stat().st_size}\t{sha256(p)}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("path\tbytes\tsha256\n" + "\n".join(rows) + "\n", encoding="utf-8")
        print(f"wrote {len(rows)} entries to {target}")
    elif mode == "check":
        lines = target.read_text(encoding="utf-8").splitlines()[1:]
        changed = missing = 0
        for line in lines:
            rel, size, digest = line.split("\t")
            p = ROOT / rel
            if not p.exists():
                missing += 1
                print("MISSING", rel)
            elif sha256(p) != digest:
                changed += 1
                print("CHANGED", rel)
        print(f"{len(lines)} archived files checked: {changed} changed, {missing} missing")
    else:
        sys.exit("mode must be write or check")


if __name__ == "__main__":
    main()
