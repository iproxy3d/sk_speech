#!/usr/bin/env python3
"""Offline Markdown-only corpus integrity test; no network or GitHub Actions."""
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "author-documents"
SPECS = (
    ("два типа речи.docx", "two-types-of-speech", 18, 0, 12, 0, 0),
    ("Форма1.docx", "speech-language-origins", 0, 694, 0, 0, 0),
    ("Шестислойная модель.docx", "six-layer-model", 0, 381, 56, 3, 17),
)
ANCHOR = re.compile(r'<a\s+id="([^"]+)"\s*></a>')
LINK = re.compile(r'!?\[[^\]]*\]\((?:<([^>]+)>|([^)]*))\)')
IMAGE = re.compile(r'!\[[^\]]*\]\(([^)]+)\)')

def git_blob_hash(path):
    h = hashlib.sha1()
    h.update(f"blob {path.stat().st_size}".encode("ascii") + bytes([0]))
    with path.open("rb") as src:
        for chunk in iter(lambda: src.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    problems = []
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    index = {row["name"]: row for row in manifest["files"]}
    for old_name, slug, pages, blocks, figures, tables, sections in SPECS:
        row = index[old_name]
        md_path = DOCS / slug / "README.md"
        if not md_path.is_file():
            problems.append(f"Missing Markdown: {slug}")
            continue
        md = md_path.read_text(encoding="utf-8")
        anchors = ANCHOR.findall(md)
        if len(anchors) != len(set(anchors)):
            problems.append(f"Repeated anchors: {slug}")
        for prefix, expected, pattern in (
            ("pages", pages, r"page-\d+"),
            ("blocks", blocks, r"B\d{3}"),
            ("figures", figures, r"figure-\d+"),
            ("tables", tables, r"table-\d+"),
            ("sections", sections, r"S\d{2}"),
        ):
            got = {a for a in anchors if re.fullmatch(pattern, a)}
            if len(got) != expected:
                problems.append(f"{slug} {prefix}: {len(got)}/{expected}")
            if prefix == "blocks" and got != {f"B{i:03d}" for i in range(1, expected + 1)}:
                problems.append(f"{slug}: incomplete block range")
            if prefix == "pages" and got != {f"page-{i}" for i in range(1, expected + 1)}:
                problems.append(f"{slug}: incomplete page range")
        if len(IMAGE.findall(md)) != figures:
            problems.append(f"{slug}: image references: {len(IMAGE.findall(md))}/{figures}")
        if row.get("markdown") != f"author-documents/{slug}/README.md":
            problems.append(f"{slug}: invalid manifest markdown path")
        blobs = row.get("media_git_blobs", {})
        if len(blobs) != figures:
            problems.append(f"{slug}: media count {len(blobs)}/{figures}")
        for image_name, expected_sha in blobs.items():
            path = DOCS / slug / "media" / image_name
            if not path.is_file() or git_blob_hash(path) != expected_sha:
                problems.append(f"{slug}: missing/modified media: {image_name}")
        old_path = ROOT / "raw" / old_name
        if old_path.exists() or (DOCS / slug / "index.html").exists():
            problems.append(f"{slug}: obsolete source file still present")
    for doc in ROOT.rglob("*.md"):
        content = doc.read_text(encoding="utf-8")
        for enclosed, regular in LINK.findall(content):
            href = enclosed.strip() if enclosed else regular.strip().split(' "', 1)[0].split(" \'", 1)[0]
            if not href:
                continue
            url = urlsplit(href)
            if url.scheme or url.netloc or href.startswith("//"):
                continue
            target = ((doc.parent / unquote(url.path)).resolve() if url.path else doc.resolve())
            if not target.exists():
                problems.append(f"Broken link in {doc.relative_to(ROOT)}: {href}")
            if target.suffix.lower() in (".docx", ".html"):
                problems.append(f"Obsolete source link in {doc.relative_to(ROOT)}: {href}")
            if url.fragment and target.is_file() and target.suffix == ".md" and re.fullmatch(r"B\d{3}|page-\d+|figure-\d+|table-\d+|S\d{2}", unquote(url.fragment)):
                if unquote(url.fragment) not in ANCHOR.findall(target.read_text(encoding="utf-8")):
                    problems.append(f"Missing anchor in {target.relative_to(ROOT)}: {url.fragment}")
    history = ROOT / "raw" / "История - весь список ссылок и описаний.txt"
    if not history.is_file() or hashlib.sha256(history.read_bytes()).hexdigest() != index[history.name]["sha256"]:
        problems.append("Original TXT history missing or altered")
    print("PASS" if not problems else "FAIL", f"({len(problems)} issues)")
    for p in problems:
        print(" -", p)
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main())
