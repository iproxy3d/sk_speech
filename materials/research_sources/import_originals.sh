#!/usr/bin/env bash
# Import the three unchanged source files. Usage:
#   bash materials/research_sources/import_originals.sh /path/to/source_files
set -euo pipefail
SRC="${1:-.}"
ROOT="$(git rev-parse --show-toplevel)"
DST="$ROOT/materials/research_sources/raw"
mkdir -p "$DST"
python3 - "$SRC" "$DST" <<'PY'
from pathlib import Path
import hashlib, shutil, sys
source, destination = map(Path, sys.argv[1:])
checksums = {
    "два типа речи.docx": "ccac7e1fe6b1bfd55bab2277a6ce688ece57b16d81308fa3d896cea19d5233c0",
    "История - весь список ссылок и описаний.txt": "0871e84b9c72f9148665756fe5298a6280d61a1d1d69911762bb332bedc16dba",
    "Теория_возникновения_языков_и_речи.docx": "2237ccabb40e7139091338f3ca97e76c43b0e7ce05ff8fa037afc793f31b08b3",
}
# Validate every source before copying any file.
for filename, sha in checksums.items():
    path = source / filename
    if not path.is_file():
        raise SystemExit(f"Missing: {path}")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != sha:
        raise SystemExit(f"SHA-256 mismatch: {path}\n expected: {sha}\n actual:   {actual}")
for filename in checksums:
    src = source / filename
    dst = destination / filename
    if dst.exists() and dst.read_bytes() != src.read_bytes():
        raise SystemExit(f"Refusing to overwrite different existing file: {dst}")
    if not dst.exists():
        shutil.copy2(src, dst)
    print(f"Verified: {dst}")
PY
git -C "$ROOT" add -- "materials/research_sources/raw"
if ! git -C "$ROOT" diff --cached --quiet -- "materials/research_sources/raw"; then
    # Commit only the imported originals; preserve unrelated staged changes.
    git -C "$ROOT" commit --only -m "docs: import immutable research source originals" -- "materials/research_sources/raw"
    git -C "$ROOT" push
else
    echo "All originals are already present; nothing to commit."
fi
