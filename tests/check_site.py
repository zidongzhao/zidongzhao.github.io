# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Checks every testable rule in SPEC.md. Run: uv run tests/check_site.py"""

import re
import sys
from pathlib import Path

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
