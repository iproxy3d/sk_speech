#!/usr/bin/env python3
"""Offline structural validation of the three stage-4 HTML editions.
Requires a complete local checkout; no HTTP, network, CI, or Actions.
This checks files/anchors and original bytes, not pixel rendering in a browser.
"""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

BASE = Path(__file__).resolve().parent.parent
DOCS = BASE / "author-documents"
CASES = (
    ("два типа речи.docx", "two-types-of-speech", "два типа речи.extracted.md", 18, 12, None),
    ("Форма1.docx", "forma1", "Форма1.extracted.md", None, 0, 694),
    ("Шестислойная модель.docx", "six-layer-model", "Шестислойная модель.extracted.md", None, 56, 381),
)

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.images = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for key in ("id", "name"):
            if a.get(key) is not None:
                self.ids.append(a[key])
        for key in ("href", "src"):
            if a.get(key):
                self.links.append(a[key])
        if tag == "img":
            self.images.append(a)

def file_hash(path, kind):
    h = hashlib.new(kind)
    if kind == "sha1":
        h.update(f"blob {path.stat().st_size}\0".encode("ascii"))
    with path.open("rb") as f:
        for data in iter(lambda: f.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()

def main():
    errors = []
    data = json.loads((BASE / "manifest.json").read_text(encoding="utf-8"))
    records = {row["name"]: row for row in data["files"]}
    if len(records) != 4:
        errors.append("Manifest must contain 4 original files")
    for name, row in records.items():
        source = BASE / "raw" / name
        if not source.is_file():
            errors.append(f"Missing original: {source}")
        elif (source.stat().st_size != row["size"]
              or file_hash(source, "sha256") != row["sha256"]
              or file_hash(source, "sha1") != row["git_blob_sha1"]):
            errors.append(f"Original checksum mismatch: {name}")
    for name, slug, snapname, pages, nimages, nblocks in CASES:
        page = DOCS / slug / "index.html"
        snap = BASE / "snapshots" / snapname
        review = DOCS / slug / "review.md"
        orig = BASE / "raw" / name
        if not all(p.is_file() for p in (page, snap, review, orig)):
            errors.append(f"Missing HTML, snapshot, review or original: {slug}")
            continue
        if records.get(name, {}).get("snapshot") != "snapshots/" + snapname:
            errors.append(f"Manifest snapshot path incorrect: {name}")
        parser = Parser()
        parser.feed(page.read_text(encoding="utf-8"))
        if len(parser.ids) != len(set(parser.ids)):
            errors.append(f"Duplicate HTML id: {slug}")
        if len(parser.images) != nimages or any("alt" not in i for i in parser.images):
            errors.append(f"Images or alt mismatch: {slug}")
        valid_links = 0
        docx_link = False
        for link in parser.links:
            uri = urlsplit(link)
            if uri.scheme or uri.netloc or link.startswith("//"):
                continue
            if unquote(uri.path).endswith(".docx"):
                docx_link = True
            target = ((page.parent / unquote(uri.path)).resolve()
                      if uri.path else page.resolve())
            if not target.is_file():
                errors.append(f"Broken relative link {slug}: {link}")
                continue
            if uri.fragment and target == page.resolve():
                if unquote(uri.fragment) not in parser.ids:
                    errors.append(f"Broken fragment {slug}: {link}")
            valid_links += 1
        if not docx_link:
            errors.append(f"No local original DOCX link: {slug}")
        text = snap.read_text(encoding="utf-8")
        if pages:
            indices = {int(v) for v in re.findall(r"#page-(\d+)", text)}
            if indices != set(range(1, pages+1)):
                errors.append(f"Page coverage {slug}: {len(indices)} of {pages}")
        elif slug == "forma1":
            indices = {int(v) for v in re.findall(r"\[B(\d{3})\]", text)}
        else:
            indices = {int(v) for v in re.findall(r"(?m)^## B(\d{3}) \(S\d+\)", text)}
        if nblocks:
            if indices != set(range(1, nblocks+1)):
                errors.append(f"Search snapshot incomplete: {slug}")
            missing = [i for i in range(1, nblocks+1) if f"B{i:03d}" not in parser.ids]
            if missing:
                errors.append(f"HTML B anchors incomplete: {slug}: {missing[:3]}")
        with ZipFile(orig) as archive:
            media = [x for x in archive.namelist() if x.startswith("word/media/") and not x.endswith("/")]
            if len(media) != nimages:
                errors.append(f"DOCX media count unexpected: {slug}")
            for entry in media:
                dest = DOCS / slug / "media" / Path(entry).name
                if not dest.is_file() or dest.read_bytes() != archive.read(entry):
                    errors.append(f"Original vs local PNG/JPEG mismatch: {slug}/{entry}")
        print(f"{slug}: {len(parser.ids)} anchors, {nimages} images, {valid_links} local links")
    if not (DOCS / "six-layer-model" / "formulas-search-4.14.md").is_file():
        errors.append("Searchable diagram formulas missing")
    if errors:
        print("FAIL", len(errors), "issues", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("PASS: offline structural checks and original-media byte comparisons")
    return 0

if __name__ == "__main__":
    sys.exit(main())
