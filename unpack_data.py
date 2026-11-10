"""Verify and unpack compressed release data with the Python standard library."""
import argparse
import gzip
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
LINE = re.compile(r"^([0-9a-f]{64})  (.+)$")


def safe_path(value):
    path = PurePosixPath(value)
    if (path.is_absolute() or not value or any(p in (".", "..", ".git") for p in path.parts)
            or "\\" in value or ":" in value):
        raise ValueError(f"Unsafe manifest path: {value}")
    target = ROOT.joinpath(*path.parts)
    for i in range(1, len(path.parts) + 1):
        if ROOT.joinpath(*path.parts[:i]).is_symlink():
            raise ValueError(f"Symlink in manifest path: {value}")
    return target


def checksum(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def read_manifest():
    sections = {"files": {}, "uncompressed": {}}
    section = None
    for line in (ROOT / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        if line in ("# files", "# uncompressed"):
            section = line[2:]
        elif line and not line.startswith("#"):
            match = LINE.fullmatch(line)
            if section is None or not match:
                raise ValueError("Invalid checksum manifest")
            h, name = match.groups()
            safe_path(name)
            if name in sections[section]:
                raise ValueError(f"Duplicate manifest entry: {name}")
            sections[section][name] = h
    return sections


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remove-gz", action="store_true", help="remove each verified archive after unpacking")
    args = parser.parse_args()
    try:
        manifest = read_manifest()
        expected = {name for name in manifest["files"]
                    if name.endswith(".gz") and name.split("/", 1)[0] in {"data", "results"}}
        actual = {p.relative_to(ROOT).as_posix() for top in ("data", "results")
                  if (ROOT / top).exists() for p in (ROOT / top).rglob("*.gz") if p.is_file()}
        if actual - expected:
            raise ValueError(f"Archives absent from manifest: {', '.join(sorted(actual - expected))}")
        if {name[:-3] for name in expected} != set(manifest["uncompressed"]):
            raise ValueError("Archive and uncompressed manifest entries do not match")
        unpacked = skipped = removed = 0
        for name in sorted(expected):
            archive = safe_path(name)
            output = safe_path(name[:-3])
            wanted = manifest["uncompressed"][name[:-3]]
            if not archive.exists():
                if output.is_file() and checksum(output) == wanted:
                    skipped += 1
                    continue
                raise ValueError(f"Missing archive and verified output: {name}")
            if checksum(archive) != manifest["files"][name]:
                raise ValueError(f"Archive checksum mismatch: {name}")
            if output.is_file() and checksum(output) == wanted:
                skipped += 1
            else:
                output.parent.mkdir(parents=True, exist_ok=True)
                temp = None
                try:
                    with tempfile.NamedTemporaryFile(dir=output.parent, delete=False) as tmp:
                        temp = Path(tmp.name)
                        h = hashlib.sha256()
                        with gzip.open(archive, "rb") as source:
                            for block in iter(lambda: source.read(1024 * 1024), b""):
                                h.update(block)
                                tmp.write(block)
                    if h.hexdigest() != wanted:
                        raise ValueError(f"Uncompressed checksum mismatch: {name}")
                    os.replace(temp, output)
                    temp = None
                    unpacked += 1
                finally:
                    if temp is not None:
                        temp.unlink(missing_ok=True)
            if args.remove_gz:
                archive.unlink()
                removed += 1
        print(f"Unpacked: {unpacked}; already verified: {skipped}; archives removed: {removed}")
    except (OSError, ValueError, EOFError) as exc:
        print(f"Unpacking failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
