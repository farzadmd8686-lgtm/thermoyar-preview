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
    if name == "errors-v33-validation-staging.html":
        # Replace browser-native alert (which displays the workers.dev hostname)
        # with a lightweight accessible Persian dialog. No call-hour logic changes.
        old = "alert('ساعت پاسخ‌گویی ترمویار از ۱۰ تا ۲۲ به وقت تهران است.');"
        if html.count(old) != 1:
            raise ValueError("Expected one call-hours alert in errors page")
        html = html.replace(old, "showCallHoursMessage();")
        html = html.replace("</head>", """<style id="call-hours-dialog-style">
#ty-hours-dialog{position:fixed;inset:0;z-index:99999;display:none;align-items:center;justify-content:center;background:rgba(0,0,0,.55);padding:20px}
#ty-hours-dialog[data-open="true"]{display:flex}
#ty-hours-dialog .ty-hours-panel{width:min(100%,420px);background:white;border-radius:20px;padding:28px 22px;text-align:center;box-shadow:0 12px 35px rgba(0,0,0,.25);font-family:Tahoma,sans-serif;color:#0d2b4d}
#ty-hours-dialog button{margin-top:20px;padding:10px 34px;border:0;border-radius:12px;background:#97051f;color:#fff;font:inherit;cursor:pointer}
</style></head>""", 1)
        html = html.replace("</body>", """<div id="ty-hours-dialog" role="alertdialog" aria-modal="true" aria-labelledby="ty-hours-title" data-open="false">
<div class="ty-hours-panel"><p id="ty-hours-title">ساعت پاسخ‌گویی ترمویار از ۱۰ تا ۲۲ به وقت تهران است.</p><button type="button" id="ty-hours-close">تأیید</button></div>
</div><script>
function showCallHoursMessage(){
 const d=document.getElementById('ty-hours-dialog');d.dataset.open='true';
 document.getElementById('ty-hours-close').focus();
}
document.getElementById('ty-hours-close').addEventListener('click',()=>{document.getElementById('ty-hours-dialog').dataset.open='false'});
document.getElementById('ty-hours-dialog').addEventListener('click',e=>{if(e.target===e.currentTarget)e.currentTarget.dataset.open='false'});
document.addEventListener('keydown',e=>{if(e.key==='Escape')document.getElementById('ty-hours-dialog').dataset.open='false'});
</script></body>""", 1)
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
