# /// script
# requires-python = ">=3.11"
# dependencies = ["pypdf"]
# ///
"""Checks every testable rule in SPEC.md. Run: uv run tests/check_site.py"""

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
# Never served: excluded by _config.yml, gitignored, or not part of the site.
NOT_SERVED = {"old-site", "tests", "docs", ".git", ".superpowers", "SPEC.md", "SOURCES.md", "CLAUDE.md", "README.md", "_config.yml"}
TEXT_SUFFIXES = {".html", ".css", ".js", ".xml", ".txt", ".md", ".yml"}

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))


def read(path: Path | str) -> str:
    return (ROOT / path).read_text(encoding="utf-8", errors="replace")


def served_files() -> list[Path]:
    out = []
    for p in ROOT.rglob("*"):
        rel = p.relative_to(ROOT)
        if p.is_file() and rel.parts[0] not in NOT_SERVED and not rel.parts[0].startswith("."):
            out.append(p)
    return out


def served_text_files() -> list[Path]:
    return [p for p in served_files() if p.suffix in TEXT_SUFFIXES]


def test_archive():
    for f in ["index.html", "research.html", "files/CV_Zidong Zhao_041621.pdf",
              "backup_20250322_112858/index.html", "Resume_Zidong Zhao_ds1p.pdf"]:
        check(f"archive has old-site/{f}", (ROOT / "old-site" / f).exists())
    pages = [p for p in (ROOT / "old-site").rglob("*.html") if p.name != "google60a4458eb7076ec4.html"]
    missing = [str(p.relative_to(ROOT)) for p in pages if '<meta name="robots" content="noindex">' not in p.read_text(errors="replace")]
    check("archive pages are noindex", bool(pages) and not missing, ", ".join(missing[:5]))
    # Zidong asked for this personal image to be removed from the public repo.
    check("removed personal image stays gone", not list(ROOT.rglob("maxkare.png")))
    robots = (ROOT / "robots.txt").read_text() if (ROOT / "robots.txt").exists() else ""
    check("robots.txt disallows /old-site/", "Disallow: /old-site/" in robots.splitlines())


def test_repo_hygiene():
    gi = read(".gitignore").splitlines() if (ROOT / ".gitignore").exists() else []
    check(".gitignore covers SOURCES.md", "SOURCES.md" in gi)
    check(".gitignore covers .superpowers/", ".superpowers/" in gi)
    cfg = read("_config.yml") if (ROOT / "_config.yml").exists() else ""
    excluded = re.findall(r"^\s*-\s*(\S+)", cfg, re.M)
    for name in ["SPEC.md", "SOURCES.md", "CLAUDE.md", "README.md", "docs", "tests"]:
        check(f"_config.yml excludes {name}", name in excluded)
    check("Search Console file at root", (ROOT / "google60a4458eb7076ec4.html").exists())
    dashed = [str(p.relative_to(ROOT)) for p in served_text_files() if "—" in p.read_text(errors="replace")]
    check("no em dashes in served files", not dashed, ", ".join(dashed))


class _Tags(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.found: list[tuple[str, dict]] = []

    def handle_starttag(self, tag, attrs):
        self.found.append((tag, {k: (v or "") for k, v in attrs}))


def tags(html: str) -> list[tuple[str, dict]]:
    p = _Tags()
    p.feed(html)
    return p.found


def index() -> str:
    return read("index.html") if (ROOT / "index.html").exists() else ""


def css() -> str:
    return read("css/site.css") if (ROOT / "css/site.css").exists() else ""


SECTION_IDS = ["about", "experience", "projects", "resume", "academics", "contact"]


def test_structure():
    html = index()
    t = tags(html)
    check("html lang=en", any(n == "html" and a.get("lang") == "en" for n, a in t))
    check("title is Zidong Zhao", re.search(r"<title>\s*Zidong Zhao\s*</title>", html) is not None)
    check("meta description", any(n == "meta" and a.get("name") == "description" and a.get("content") for n, a in t))
    ids = [a["id"] for n, a in t if n == "section" and "id" in a]
    check("six sections in order", ids == SECTION_IDS, str(ids))
    nav_start = html.find('id="site-nav"')
    nav_html = html[nav_start: html.find("</nav>", nav_start)] if nav_start >= 0 else ""
    hrefs = [a["href"] for n, a in tags(nav_html) if n == "a"]
    check("nav links match sections", hrefs == ["#" + i for i in SECTION_IDS], str(hrefs))
    check("skip link to #main", any(n == "a" and "skip" in a.get("class", "") and a.get("href") == "#main" for n, a in t))
    check("main#main", any(n == "main" and a.get("id") == "main" for n, a in t))
    check("nav toggle aria", any(n == "button" and a.get("id") == "nav-toggle" and a.get("aria-controls") == "site-nav"
                                 and a.get("aria-expanded") == "false" for n, a in t))


def test_fonts():
    links = [a.get("href", "") for n, a in tags(index()) if n == "link" and "fonts.googleapis.com/css2" in a.get("href", "")]
    main = [h for h in links if "Newsreader" in h and "IBM+Plex+Sans" in h and "display=swap" in h]
    check("Google Fonts link for Newsreader + Plex", len(main) == 1, str(links))
    cjk = [h for h in links if "Noto+Serif+SC" in h]
    text = unquote(parse_qs(urlparse(cjk[0].replace("&amp;", "&")).query).get("text", [""])[0]) if cjk else ""
    check("Noto Serif SC limited to 赵紫东", text == "赵紫东", text)
    c = css()
    check("serif fallback Georgia", re.search(r"Newsreader[^;]*Georgia", c) is not None)
    check("sans fallback system-ui", re.search(r"IBM Plex Sans[^;]*system-ui", c) is not None)
    check("font-size-adjust used", "font-size-adjust" in c)


def _tokens(block: str) -> dict[str, str]:
    return dict(re.findall(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{6})", block))


def _luminance(hex_: str) -> float:
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hex_[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a: str, b: str) -> float:
    la, lb = sorted([_luminance(a), _luminance(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def test_contrast():
    c = css()
    light = re.search(r"^:root\s*\{([^}]*)\}", c, re.M)
    dark = re.search(r"@media\s*\(prefers-color-scheme:\s*dark\)\s*\{\s*:root\s*\{([^}]*)\}", c)
    check("light and dark token blocks", bool(light and dark))
    if not (light and dark):
        return
    for mode, block in [("light", light.group(1)), ("dark", dark.group(1))]:
        tok = _tokens(block)
        for fg in ["--ink", "--body", "--muted", "--accent"]:
            for bg in ["--bg", "--card"]:
                if fg in tok and bg in tok:
                    r = contrast(tok[fg], tok[bg])
                    check(f"{mode} {fg} on {bg} >= 4.5", r >= 4.5, f"{r:.2f}")
                else:
                    check(f"{mode} has {fg} and {bg}", False)


def test_analytics():
    check("GA tag present", "G-L9Q1GGPFNJ" in index())


def section(sid: str) -> str:
    html = index()
    start = html.find(f'<section id="{sid}"')
    return html[start: html.find("</section>", start)] if start >= 0 else ""


def visible_text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


POSITIONING = "Bridging human behavior and complex technical systems, turning experience into measurable signals and product decisions."
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}")
FOCUS = ["UX Research", "Product Data Science", "Behavioral Insights"]
PHONE_RE =re.compile(r"\(?\b\d{3}\)?[ .-]?\d{3}[ .-]?\d{4}\b")


def test_copy():
    check("About has positioning line", POSITIONING in visible_text(section("about")))
    texts = {p: p.read_text(errors="replace") for p in served_text_files()}
    emails = [str(p.relative_to(ROOT)) for p, t in texts.items() if EMAIL_RE.search(t) or "mailto:" in t]
    check("no email address or mailto in served files", not emails, ", ".join(emails))
    phones = [str(p.relative_to(ROOT)) for p, t in texts.items() if PHONE_RE.search(visible_text(t))]
    check("no phone number in served files", not phones, ", ".join(phones))
    check("Contact shows obfuscated email", "zhaozidong1993 at gmail dot com" in visible_text(section("contact")))
    exp = section("experience")
    cards = re.findall(r'<article class="card[^"]*"[^>]*>(.*?)</article>', exp, re.S)
    orgs = ["Instagram", "HelloNova", "Yale", "Princeton"]
    check("four experience cards", len(cards) == 4, str(len(cards)))
    check("experience order", len(cards) == 4 and all(o in visible_text(c) for o, c in zip(orgs, cards)))
    paras = re.findall(r"<p[^>]*>(.*?)</p>", section("academics"), re.S)
    check("Academics opens with 'In a previous life'", bool(paras) and "In a previous life" in paras[0])
    check("no posters in Academics", "poster" not in section("academics").lower())
    focus = re.search(r'<ul class="focus"[^>]*>(.*?)</ul>', index(), re.S)
    items = [visible_text(i).strip() for i in re.findall(r"<li>(.*?)</li>", focus.group(1), re.S)] if focus else []
    check("sidebar focus line", items == FOCUS, str(items))
    check("old tagline removed", "Making human experience measurable" not in index())
    desc = next((a.get("content", "") for n, a in tags(index()) if n == "meta" and a.get("name") == "description"), "")
    check("meta description mentions product data science", "product data science" in desc)
    check("About toolkit names DS skills", all(k in visible_text(section("about")) for k in ["A/B testing", "causal inference", "SQL"]))


def _has_exif(data: bytes) -> bool:
    i = 2
    while i + 4 <= len(data) and data[i] == 0xFF:
        marker, length = data[i + 1], int.from_bytes(data[i + 2:i + 4], "big")
        if marker == 0xE1 and data[i + 4:i + 8] == b"Exif":
            return True
        if marker == 0xDA:
            break
        i += 2 + length
    return False


def test_photo():
    imgs = [a for n, a in tags(section("about")) if n == "img"]
    check("About has one photo", len(imgs) == 1)
    if not imgs:
        return
    a = imgs[0]
    check("photo src is assets/photo.jpg", a.get("src") == "assets/photo.jpg")
    check("photo has alt text", len(a.get("alt", "")) > 5)
    check("photo has width and height", a.get("width", "").isdigit() and a.get("height", "").isdigit())
    f = ROOT / "assets/photo.jpg"
    data = f.read_bytes() if f.exists() else b""
    check("photo file under 200 KB", 0 < len(data) < 200_000, f"{len(data)} bytes")
    # Phone photos carry EXIF (location, device); the public copy must not.
    check("photo has no EXIF metadata", bool(data) and not _has_exif(data))


DOIS = ["10.1016/j.jesp.2023.104521", "10.1037/emo0000890", "10.1017/S0140525X19003133",
        "10.1037/xge0000565", "10.1080/02699931.2015.1110117"]
RESUME = "assets/Zidong-Zhao-Resume.pdf"


def test_projects():
    proj = section("projects")
    card = re.search(r'<article class="card[^"]*"[^>]*>(.*?)</article>', proj, re.S)
    body = card.group(1) if card else ""
    btns = [a for n, a in tags(body) if n == "button"]
    check("portfolio card has disabled Coming soon button",
          "Coming soon" in visible_text(body) and any("disabled" in a for a in btns) and "href" not in body)
    pubs = re.findall(r'<li class="pub">(.*?)</li>', proj, re.S)
    check("five publications", len(pubs) == 5, str(len(pubs)))
    for i, pub in enumerate(pubs):
        hrefs = [a.get("href", "") for n, a in tags(pub) if n == "a"]
        pdfs = [h for h in hrefs if h.startswith("files/")]
        dois = [h for h in hrefs if h.startswith("https://doi.org/")]
        check(f"pub {i + 1} has one existing PDF", len(pdfs) == 1 and (ROOT / pdfs[0].split("#")[0]).exists(), str(pdfs))
        check(f"pub {i + 1} has one DOI", len(dois) == 1, str(dois))
        check(f"pub {i + 1} journal italic", re.search(r"<(i|em)>", pub) is not None)
    for d in DOIS:
        check(f"DOI {d} linked", f"https://doi.org/{d}" in proj)
    check("BBS opens at page 52", "files/BBS2020_PredictiveSubstrate.pdf#page=52" in proj)
    check("Thornton opens at page 2", "files/ZhaoThorntonTamir2020.pdf#page=2" in proj)
    # Scholar and old CVs link straight to /files/<paper>.pdf; GitHub Pages cannot redirect PDFs.
    for n in ["ZhaoSenedTamir2023", "ZhaoThorntonTamir2020", "BBS2020_PredictiveSubstrate", "MeyerZhaoTamir2019", "OlatunjiBergZhao2017"]:
        check(f"old PDF URL files/{n}.pdf still served", (ROOT / "files" / f"{n}.pdf").exists())
    check("old CV PDF not republished", not (ROOT / "files/CV_Zidong Zhao_041621.pdf").exists())


def test_resume():
    res = section("resume")
    t = tags(res)
    embeds = [i for i, (n, a) in enumerate(t) if n in ("embed", "object") and RESUME in (a.get("src", "") + a.get("data", ""))]
    dls = [i for i, (n, a) in enumerate(t) if n == "a" and "btn" in a.get("class", "") and "download" in a
           and a.get("href") == RESUME]
    check("resume embed", bool(embeds))
    check("download button before embed", bool(dls and embeds) and dls[0] < embeds[0])
    # Android Chrome and plugin-less browsers can't render inline PDFs; <object> shows its fallback instead.
    obj = re.search(r"<object[^>]*>(.*?)</object>", res, re.S)
    check("resume viewer has a download fallback", bool(obj) and RESUME in obj.group(1) and "download" in obj.group(1))
    pdf = ROOT / RESUME
    check("resume PDF exists", pdf.exists())
    if pdf.exists():
        from pypdf import PdfReader
        text = " ".join(page.extract_text() or "" for page in PdfReader(pdf).pages)
        check("resume PDF has text", len(text) > 500, str(len(text)))
        check("resume PDF has no phone number", PHONE_RE.search(text) is None)


def test_interactions():
    c = css()
    rm = re.search(r"@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{(.*?)\n\}", c, re.S)
    block = rm.group(1) if rm else ""
    check("reduced-motion block", bool(rm))
    for sel in [".card", ".social a", ".prose a"]:
        check(f"reduced motion covers {sel}", sel in block)
    check("reduced motion disables transition and transform", "transition: none" in block and "transform: none" in block)
    check(":focus-visible styles", ":focus-visible" in c)
    check("focus items never break mid-phrase", re.search(r"\.focus li\s*\{[^}]*white-space:\s*nowrap", c) is not None)
    check("social row spaced from nav", re.search(r"\.social\s*\{[^}]*margin-top", c) is not None)
    hide = re.findall(r"([^{}]*#site-nav[^{}]*)\{[^}]*display:\s*none", c)
    check("mobile menu only collapses with JS", bool(hide) and all(".js" in s for s in hide), str(hide))
    links = re.findall(r"<a ([^>]*)>\s*(<svg[^>]*>)", re.search(r'<div class="social">(.*?)</div>', index(), re.S).group(1)
                       if '<div class="social">' in index() else "")
    check("three social icon links", len(links) == 3, str(len(links)))
    check("social links labelled, icons hidden", all("aria-label=" in a and 'aria-hidden="true"' in s for a, s in links))
    js = read("js/site.js") if (ROOT / "js/site.js").exists() else ""
    check("js adds .js class", "classList.add('js')" in js or 'classList.add("js")' in js)
    check("tilt gated on fine pointer", "(pointer: fine)" in js)
    check("tilt gated on reduced motion", "prefers-reduced-motion" in js)
    check("menu toggles aria-expanded", "aria-expanded" in js)
    check("active nav uses aria-current", "aria-current" in js and "IntersectionObserver" in js)
    check("script loaded with defer", re.search(r'<script src="js/site.js" defer', index()) is not None)
    check("failed site.js load restores the open menu", re.search(r'<script src="js/site.js" defer onerror="[^"]*classList\.remove\(\'js\'\)', index()) is not None)


REDIRECTS = {
    "cv.html": "resume", "publications.html": "projects", "research.html": "academics",
    "collaborators.html": "academics", "contact.html": "contact",
    **{f"publications/{n}.html": "projects" for n in [
        "ZhaoSenedTamir2023", "ZhaoThorntonTamir2020", "ZhaoMildnerTamir2020", "MeyerZhaoTamir2019",
        "OlatunjiBergZhao2017", "sans2019", "spsp2018", "spsp2019"]},
}


def test_redirects():
    for path, sid in REDIRECTS.items():
        f = ROOT / path
        html = f.read_text() if f.exists() else ""
        url = f"/#{sid}"
        ok = (f'<meta http-equiv="refresh" content="0; url={url}">' in html
              and f'<link rel="canonical" href="https://zidongzhao.github.io{url}">' in html
              and '<meta name="robots" content="noindex">' in html
              and f'<a href="{url}">' in html)
        check(f"redirect {path} -> {url}", ok)
    sm = read("sitemap.xml") if (ROOT / "sitemap.xml").exists() else ""
    check("sitemap lists only the home page", re.findall(r"<loc>(.*?)</loc>", sm) == ["https://zidongzhao.github.io/"])


def test_links():
    broken, into_archive = [], []
    for p in served_files():
        if p.suffix != ".html":
            continue
        for n, a in tags(p.read_text(errors="replace")):
            ref = a.get("href") or a.get("src") or ""
            if not ref or re.match(r"^(https?:|#|data:)", ref):
                continue
            path = ref.split("#")[0].split("?")[0]
            if not path:
                continue
            target = ROOT / path.lstrip("/") if path.startswith("/") else p.parent / path
            if path.lstrip("/").startswith("old-site") or "old-site" in target.resolve().parts:
                into_archive.append(f"{p.relative_to(ROOT)} -> {ref}")
            elif not target.exists():
                broken.append(f"{p.relative_to(ROOT)} -> {ref}")
    check("no broken local links", not broken, "; ".join(broken[:5]))
    check("nothing links into old-site/", not into_archive, "; ".join(into_archive[:5]))


def main() -> None:
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    failed = [r for r in results if not r[1]]
    for name, ok, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}{'  (' + detail + ')' if detail and not ok else ''}")
    print(f"\n{len(results) - len(failed)}/{len(results)} passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
