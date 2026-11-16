#!/usr/bin/env python3
"""Offline checks for canonical Markdown editions of three author DOCX files.
Run inside a complete local checkout; no network, CI, or GitHub Actions.
It checks content markers, links, images, hashes, and legacy HTML anchor parity.
Visual rendering and an exact text-style diff are outside this structural check.
"""
import hashlib
import html.parser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "author-documents"
SPECS = (
    ("два типа речи.docx", "two-types-of-speech", 18, 0, 12, 0, 0),
    ("Форма1.docx", "forma1", 0, 694, 0, 0, 0),
    ("Шестислойная модель.docx", "six-layer-model", 0, 381, 56, 3, 17),
)
ANCHOR_RE = re.compile(r'<a\s+id="([^"]+)"\s*></a>')
IMAGE_RE = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
LINK_RE = re.compile(r'(?<!!)\[[^\]]+\]\((?:<([^>]+)>|([^)]*))\)')
TABLE_RE = re.compile(r'<a id="table-\d+"></a>')

class HTMLAnchors(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == "id":
                self.ids.append(value)

def sha_file(path, kind):
    h = hashlib.new(kind)
    if kind == "sha1":
        h.update(f"blob {path.stat().st_size}\0".encode("ascii"))
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def local_target(source, link):
    u = urlsplit(link)
    if u.scheme or u.netloc or link.startswith("//"):
        return None
    target = ((source.parent / unquote(u.path)).resolve() if u.path
              else source.resolve())
    return target, unquote(u.fragment)

def main():
    errors = []
    manifests = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    rows = {r["name"]: r for r in manifests["files"]}
    for source_name, slug, page_count, block_count, figure_count, table_count, section_count in SPECS:
        folder = DOCS / slug
        md_path = folder / "README.md"
        html_path = folder / "index.html"
        original = ROOT / "raw" / source_name
        if not all(p.is_file() for p in (md_path, html_path, original)):
            errors.append(f"Missing files for {slug}")
            continue
        manifest = rows[source_name]
        if manifest.get("markdown") != f"author-documents/{slug}/README.md":
            errors.append(f"Manifest Markdown path incorrect: {slug}")
        if original.stat().st_size != manifest["size"]:
            errors.append(f"Source size mismatch: {slug}")
        if sha_file(original, "sha256") != manifest["sha256"]:
            errors.append(f"Original SHA-256 mismatch: {slug}")
        if sha_file(original, "sha1") != manifest["git_blob_sha1"]:
            errors.append(f"Original Git SHA-1 mismatch: {slug}")
        md = md_path.read_text(encoding="utf-8")
        anchors = ANCHOR_RE.findall(md)
        ids = set(anchors)
        html_parser = HTMLAnchors()
        html_parser.feed(html_path.read_text(encoding="utf-8"))
        legacy = {i for i in html_parser.ids if re.fullmatch(
            r"B\d{3}|page-\d+|S\d{2}|figure-\d+|table-\d+", i)}
        current = {i for i in ids if re.fullmatch(
            r"B\d{3}|page-\d+|S\d{2}|figure-\d+|table-\d+", i)}
        if current != legacy:
            errors.append(f"Legacy anchor mismatch for {slug}: {len(current)} vs {len(legacy)}")
        if len(anchors) != len(ids):
            errors.append(f"Duplicate Markdown anchors for {slug}")
        for kind, expected, pattern in (
            ("page", page_count, r"page-\d+"),
            ("block", block_count, r"B\d{3}"),
            ("figure", figure_count, r"figure-\d+"),
            ("table", table_count, r"table-\d+"),
            ("section", section_count, r"S\d{2}"),
        ):
            found = {a for a in ids if re.fullmatch(pattern, a)}
            if len(found) != expected:
                errors.append(f"{slug} {kind}: {len(found)}/{expected}")
            if kind == "block" and found != {f"B{i:03d}" for i in range(1, expected+1)}:
                errors.append(f"{slug} incomplete numbered blocks")
            if kind == "page" and found != {f"page-{i}" for i in range(1, expected+1)}:
                errors.append(f"{slug} incomplete pages")
        images = IMAGE_RE.findall(md)
        if len(images) != figure_count:
            errors.append(f"{slug}: {len(images)} Markdown images, expected {figure_count}")
        if len(TABLE_RE.findall(md)) != table_count:
            errors.append(f"{slug}: Markdown table anchor count mismatch")
        for alt, uri in images:
            if not alt.strip():
                errors.append(f"{slug}: image missing alt")
            resolved = local_target(md_path, uri)
            if resolved is None or not resolved[0].is_file():
                errors.append(f"{slug}: missing image {uri}")
        links = LINK_RE.findall(md)
        for angle, ordinary in links:
            uri = angle or ordinary
            ref = local_target(md_path, uri)
            if ref is None:
                continue
            target, fragment = ref
            if not target.is_file():
                errors.append(f"{slug}: broken local link {uri}")
            if fragment and target == md_path and fragment not in ids:
                errors.append(f"{slug}: broken Markdown fragment {uri}")
        with ZipFile(original) as archive:
            original_media = [p for p in archive.namelist()
                              if p.startswith("word/media/") and not p.endswith("/")]
            if len(original_media) != figure_count:
                errors.append(f"{slug}: ZIP image count mismatch")
            for entry in original_media:
                image_path = folder / "media" / Path(entry).name
                if not image_path.is_file() or image_path.read_bytes() != archive.read(entry):
                    errors.append(f"{slug}: media differs from DOCX: {entry}")
        print(f"{slug}: {len(current)} anchors; {len(images)} figures; {len(links)} links")
    if errors:
        print("FAIL:", len(errors), "errors", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("PASS: Markdown/HTML anchor parity, links, images, original DOCX checksums")
    return 0

if __name__ == "__main__":
    sys.exit(main())
