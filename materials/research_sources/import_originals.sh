#!/usr/bin/env bash
# Import original files listed in manifest.json without modifying them.
# Usage: bash materials/research_sources/import_originals.sh /path/to/source_files
set -euo pipefail
SRC="${1:-.}"
ROOT="$(git rev-parse --show-toplevel)"
DST="$ROOT/materials/research_sources/raw"
mkdir -p "$DST"
python3 - "$SRC" "$DST" "$ROOT/materials/research_sources/manifest.json" <<'PY'
from pathlib import Path
import hashlib, json, shutil, sys
source, destination, manifest_path = map(Path, sys.argv[1:])
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
files = manifest["files"]
for item in files:
    path = source / item["name"]
    if not path.is_file():
        raise SystemExit(f"Missing: {path}")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != item["sha256"]:
        raise SystemExit(f"SHA-256 mismatch: {path}")
for item in files:
    src, dst = source / item["name"], destination / item["name"]
    if dst.exists() and hashlib.sha256(dst.read_bytes()).hexdigest() != item["sha256"]:
        raise SystemExit(f"Refusing to overwrite different existing file: {dst}")
    if not dst.exists():
        shutil.copy2(src, dst)
    print(f"Verified: {dst}")
PY
git -C "$ROOT" add -- "materials/research_sources/raw"
if ! git -C "$ROOT" diff --cached --quiet -- "materials/research_sources/raw"; then
    git -C "$ROOT" commit --only -m "docs: import immutable research source originals" -- "materials/research_sources/raw"
    git -C "$ROOT" push
else
    echo "All originals are already present; nothing to commit."
fi
