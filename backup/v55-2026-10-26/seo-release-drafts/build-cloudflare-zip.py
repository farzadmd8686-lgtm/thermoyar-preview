#!/usr/bin/env python3
"""Build a production ZIP from the three approved ThermoYar staging pages.
Run from repository root: python backup/v55-2026-10-26/seo-release-drafts/build-cloudflare-zip.py
Only release-specific metadata/links are changed. Original staging files remain untouched.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import re

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "seo-release-drafts" / "thermoyar-v62-v26-v33-cloudflare.zip"
SOURCES = {
    "index-v62-validation-staging.html": ("index.html", "https://thermoyar.ir/"),
    "buying-guide-v26-validation-staging.html": ("buying-guide.html", "https://thermoyar.ir/buying-guide.html"),
    "errors-v33-validation-staging.html": ("errors.html", "https://thermoyar.ir/errors.html"),
}
RENAME = {name: target for name, (target, _) in SOURCES.items()}
def build_html(name, canonical):
    html = (BASE / name).read_text(encoding="utf-8")
    html, count = re.subn(r'<meta\s+name=["\']robots["\']\s+content=["\']noindex,follow["\']\s*/?>', '', html, flags=re.I)
    if count != 1:
        raise ValueError(f"{name}: expected one staging noindex meta, found {count}")
    html, count = re.subn(r'(<link\s+rel=["\']canonical["\']\s+href=["\'])[^"\']+(["\'])', lambda m: m.group(1) + canonical + m.group(2), html, count=1, flags=re.I)
    if count != 1:
        raise ValueError(f"{name}: canonical missing")
    for old, new in RENAME.items():
        html = html.replace(old, new)
    if "validation-staging.html" in html or "github.io/thermoyar-preview" in html:
        raise ValueError(f"{name}: preview reference remains")
    return html

def main():
    pages = {target: build_html(source, canonical) for source, (target, canonical) in SOURCES.items()}
    refs = set()
    for html in pages.values():
        refs.update(re.findall(r'assets/[a-zA-Z0-9_.-]+', html))
    missing = [p for p in refs if not (BASE / p).is_file()]
    if missing:
        raise FileNotFoundError("Missing assets: " + ", ".join(sorted(missing)))
    robots = "User-agent: *\nAllow: /\nSitemap: https://thermoyar.ir/sitemap.xml\n"
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{url}</loc></url>\n" for _, url in SOURCES.values()) + "</urlset>\n"
    with ZipFile(OUT, "w", ZIP_DEFLATED) as z:
        for name, html in pages.items():
            z.writestr(name, html)
        for ref in sorted(refs):
            z.write(BASE / ref, ref)
        z.writestr("robots.txt", robots)
        z.writestr("sitemap.xml", sitemap)
    print(f"Created {OUT} ({OUT.stat().st_size:,} bytes), {len(pages)} pages, {len(refs)} assets")
if __name__ == "__main__":
    main()
