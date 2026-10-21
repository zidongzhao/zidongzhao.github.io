# zidongzhao.github.io

Zidong Zhao's personal website: a single page with experience, projects, resume, academic background, and contact. Plain HTML, CSS, and vanilla JS, published by GitHub Pages from `master`.

- Run locally: `uv run python -m http.server 8000`, then open http://localhost:8000
- Static checks: `uv run tests/check_site.py`
- Link-preview image: `uv run scripts/share_card.py` rebuilds `assets/share-card.jpg` from the page's copy, photo, and colors. The static checks fail when it is out of date.
- Pre-commit hook that runs the static checks: `git config core.hooksPath .githooks` (once per clone).
- Browser checks (desktop and phone profiles): `uv run tests/browser_check.py http://127.0.0.1:8000 /tmp/shots`. First time: `uv run --with playwright playwright install chromium webkit`.

`SPEC.md` describes the design, and `docs/2026-10-19-revamp-record.md` records the October 2026 revamp. The previous version of the site lives in `old-site/` for reference.
