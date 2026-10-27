#!/usr/bin/env python3
"""Build isolated ThermoYar lazy-motion test ZIP; no production files modified."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import re
ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "backup/v55-2026-10-26"
EXP = ROOT / "experiments/lazy-motion-v62"
SOURCE = BASE / "seo-release-drafts/build-cloudflare-zip.py"
# Reuse approved production transforms; override only the V62 input location.
import importlib.util
spec = importlib.util.spec_from_file_location("thermoyar_release_builder", SOURCE)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
pages = {}
for name, (target, canonical) in builder.SOURCES.items():
    if target == "index.html":
        html = (EXP / "index-v62-lazy-motion-staging.html").read_text(encoding="utf-8")
        original = (BASE / name).read_text(encoding="utf-8")
        expected = original.replace('class="boiler" src=', 'class="boiler" loading="lazy" src=').replace('class="tech" src=', 'class="tech" loading="lazy" src=')
        if html != expected:
            raise ValueError("Experimental page differs from locked V62 beyond the two approved lazy attributes")
        # Temporarily supply the experimental content to the existing transform without writing source.
        from unittest.mock import patch
        old_read_text = Path.read_text
        def read_text(self, *args, **kwargs):
            return html if self == BASE / name else old_read_text(self, *args, **kwargs)
        with patch.object(Path, "read_text", read_text):
            pages[target] = builder.build_html(name, canonical)
    else:
        pages[target] = builder.build_html(name, canonical)
refs = set()
for html in pages.values():
    refs.update(re.findall(r'assets/[a-zA-Z0-9_.-]+', html))
missing = [ref for ref in refs if not (BASE / ref).is_file()]
if missing:
    raise FileNotFoundError("Missing assets: " + ", ".join(sorted(missing)))
out = EXP / "thermoyar-lazy-motion-test.zip"
with ZipFile(out, "w", ZIP_DEFLATED) as z:
    for name, html in pages.items():
        z.writestr(name, html)
    for ref in sorted(refs):
        z.write(BASE / ref, ref)
    # Staging must not be indexed, and must not claim production canonical URLs.
    z.writestr("robots.txt", "User-agent: *\\nDisallow: /\\n")
    for name in pages:
        pass
print(f"Built {out} with {len(pages)} pages and {len(refs)} assets")
