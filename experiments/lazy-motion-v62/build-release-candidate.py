#!/usr/bin/env python3
"""Build a production-format release CANDIDATE only. Never deploy automatically."""
from pathlib import Path
from zipfile import ZipFile
from unittest.mock import patch
import importlib.util
import re

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "backup/v55-2026-10-26"
EXP = ROOT / "experiments/lazy-motion-v62"
source = BASE / "seo-release-drafts/build-cloudflare-zip.py"
spec = importlib.util.spec_from_file_location("thermoyar_release_builder", source)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

original_name = "index-v62-validation-staging.html"
original_path = BASE / original_name
original = original_path.read_text(encoding="utf-8")
experimental = (EXP / "index-v62-lazy-motion-staging.html").read_text(encoding="utf-8")
expected = original
for marker in ('class="boiler" src=', 'class="tech" src='):
    if expected.count(marker) != 1:
        raise ValueError(f"Expected one occurrence: {marker}")
    expected = expected.replace(marker, marker.replace(" src=", ' loading="lazy" src='))
if experimental != expected:
    raise ValueError("Experimental HTML differs from approved V62 in more than two attributes")

# Use the approved release builder, with only the in-memory homepage input swapped.
# No locked source, release script, or deployed Worker is modified.
candidate = EXP / "thermoyar-lazy-motion-release-CANDIDATE.zip"
builder.OUT = candidate
original_read = Path.read_text
def substituted_read(path, *args, **kwargs):
    if path == original_path:
        return experimental
    return original_read(path, *args, **kwargs)

with patch.object(Path, "read_text", substituted_read):
    builder.main()

# Compare transformed production homepage with approved baseline byte-for-byte,
# after removing ONLY the two explicitly authorized lazy attributes.
baseline = builder.build_html(original_name, "https://thermoyar.ir/")
with ZipFile(candidate) as archive:
    assert archive.testzip() is None
    names = set(archive.namelist())
    assert {"index.html", "buying-guide.html", "errors.html", "robots.txt", "sitemap.xml"} <= names
    home = archive.read("index.html").decode("utf-8")
    assert home.replace('class="boiler" loading="lazy"', 'class="boiler"').replace(
        'class="tech" loading="lazy"', 'class="tech"') == baseline
    assert 'noindex' not in home.lower()
    assert 'rel="canonical"' in home
    assert 'https://thermoyar.ir/' in home
    assert 'loading="lazy"' in home
    for page in ("buying-guide.html", "errors.html"):
        source_name = next(n for n, (target, _) in builder.SOURCES.items() if target == page)
        canonical = builder.SOURCES[source_name][1]
        assert archive.read(page).decode("utf-8") == builder.build_html(source_name, canonical)
    assert "Disallow: /" not in archive.read("robots.txt").decode("utf-8")
    assert "https://thermoyar.ir/sitemap.xml" in archive.read("robots.txt").decode("utf-8")
    assert "https://thermoyar.ir/" in archive.read("sitemap.xml").decode("utf-8")
print("Release candidate validated: only two lazy attributes changed; SEO and other pages preserved.")
