# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
"""Builds assets/share-card.jpg, the link-preview image, from the page's own copy, photo, and colors.

Run after changing the name, 赵紫东, the focus line, the photo, or the colors: uv run scripts/share_card.py
The image carries a fingerprint of its inputs; tests/check_site.py fails when they no longer match.
"""

import hashlib
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/share-card.jpg"
PHOTO = ROOT / "assets/photo.jpg"
URL = "zidongzhao.github.io"
TOKENS = ["--bg", "--ink", "--muted", "--accent", "--card-shadow", "--paper"]
STAMP = b"share-card "


def copy() -> dict:
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    text = lambda pattern: re.sub(r"<[^>]+>", "", re.search(pattern, page, re.S).group(1)).strip()
    focus = re.search(r'<ul class="focus"[^>]*>(.*?)</ul>', page, re.S).group(1)
    return {
        "name": text(r'<h1 class="name">(.*?)</h1>'),
        "zh": text(r'<p class="name-zh"[^>]*>(.*?)</p>'),
        "focus": [re.sub(r"<[^>]+>", "", i).strip() for i in re.findall(r"<li>(.*?)</li>", focus, re.S)],
    }


def tokens() -> dict:
    css = (ROOT / "css/site.css").read_text(encoding="utf-8")
    root = re.search(r"^:root\s*\{(.*?)^\}", css, re.S | re.M).group(1)
    return {t: re.search(rf"{t}:\s*([^;]+);", root).group(1).strip() for t in TOKENS}


def fingerprint() -> str:
    h = hashlib.sha256()
    for part in [repr(copy()), repr(tokens()), URL, Path(__file__).read_text(encoding="utf-8")]:
        h.update(part.encode())
    h.update(PHOTO.read_bytes())
    return h.hexdigest()[:16]


def stamped(path: Path = OUT) -> str | None:
    """The fingerprint stored in the image's JPEG comment, if any."""
    data = path.read_bytes() if path.exists() else b""
    m = re.search(rb"\xff\xfe..(" + re.escape(STAMP) + rb"[0-9a-f]{16})", data[:4096], re.S)
    return m.group(1)[len(STAMP):].decode() if m else None


def card_html() -> str:
    c, t = copy(), tokens()
    # Separators sit between the unbreakable phrases so the line can wrap there.
    focus = " · ".join(f"<span>{html.escape(f)}</span>" for f in c["focus"])
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&family=Newsreader:opsz,wght@6..72,500&display=block">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Long+Cang&text={html.escape(c["zh"])}&display=block">
<style>
html, body {{ margin: 0; }}
body {{
  width: 1200px; height: 630px; box-sizing: border-box; padding: 0 96px; overflow: hidden;
  display: flex; align-items: center; gap: 72px;
  background-color: {t["--bg"]}; background-image: {t["--paper"]}; color: {t["--ink"]};
}}
img {{ width: 380px; height: 380px; flex-shrink: 0; border: 2.5px solid {t["--ink"]}; box-shadow: 12px 12px 0 {t["--card-shadow"]}; }}
#text {{ min-width: 0; }}
p {{ margin: 0; }}
.name {{ font: 500 84px/1 Newsreader, serif; }}
.zh {{ font: 50px/1.3 "Long Cang", serif; color: {t["--muted"]}; margin-top: 14px; }}
.focus {{ font: 600 30px/1.45 "IBM Plex Sans", sans-serif; color: {t["--accent"]}; margin-top: 34px; }}
.focus span {{ white-space: nowrap; }}
.url {{ font: 24px "IBM Plex Sans", sans-serif; color: {t["--muted"]}; margin-top: 40px; }}
</style></head><body>
<img src="{PHOTO.as_uri()}" alt="">
<div id="text">
  <p class="name">{html.escape(c["name"])}</p>
  <p class="zh" lang="zh">{html.escape(c["zh"])}</p>
  <p class="focus">{focus}</p>
  <p class="url">{URL}</p>
</div>
</body></html>"""


def main() -> None:
    from playwright.sync_api import sync_playwright

    page_file = OUT.with_suffix(".tmp.html")
    page_file.write_text(card_html(), encoding="utf-8")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1200, "height": 630})
            page.goto(page_file.as_uri(), wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            # Fallback fonts or text spilling past the card would ship silently, so stop instead.
            loaded = page.evaluate("[...document.fonts].filter(f => f.status === 'loaded').map(f => f.family.replaceAll('\"', ''))")
            missing = [f for f in ["Newsreader", "IBM Plex Sans", "Long Cang"] if f not in loaded]
            box = page.evaluate("(() => { const t = document.getElementById('text'), r = t.getBoundingClientRect();"
                                " return [r.top, r.bottom, r.left + t.scrollWidth]; })()")
            if missing or box[0] < 40 or box[1] > 590 or box[2] > 1160:
                sys.exit(f"Share card not written. Missing fonts: {missing or 'none'}; text box top, bottom, right: {box}")
            jpeg = page.screenshot(type="jpeg", quality=88)
            browser.close()
    finally:
        page_file.unlink(missing_ok=True)
    comment = STAMP + fingerprint().encode()
    segment = b"\xff\xfe" + (len(comment) + 2).to_bytes(2, "big") + comment
    OUT.write_bytes(jpeg[:2] + segment + jpeg[2:])
    print(f"Wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB), fingerprint {fingerprint()}")


if __name__ == "__main__":
    main()
