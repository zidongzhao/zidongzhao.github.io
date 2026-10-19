# /// script
# requires-python = ">=3.11"
# dependencies = []
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
