# CLAUDE.md

Zidong's personal website, served at https://zidongzhao.github.io. **Public**: everything in this repo is readable by anyone, so no secrets, no phone number, no plain email address. See `SPEC.md` for the design; `SOURCES.md` (gitignored) holds resume and LinkedIn text for copy.

## Stack and commands

- Plain HTML, CSS, vanilla JS. No framework, no build step.
- Run locally: `uv run python -m http.server 8000`, then open http://localhost:8000
- Check: `uv run tests/check_site.py`; browser checks: `uv run tests/browser_check.py http://127.0.0.1:8000 /tmp/shots` (first time: `uv run --with playwright playwright install chromium`)
- Deploy: merge into `master` and push; GitHub Pages publishes it. Ask Zidong first.

## Decisions

- Plain HTML over Astro: one page that changes a few times a year. Move to Astro only if projects grow into many pages.
- Jekyll stays on (GitHub Pages default) only so `_config.yml` can exclude project docs from the live site.
- `old-site/` is the full pre-2026 site, kept for reference. Its pages carry `noindex` and `robots.txt` disallows it. Nothing on the new site links into it. Its root-relative links are broken by design.
- Old top-level URLs redirect to sections of the new page.

## Gotchas

- SPEC.md has been edited in the IDE and by Claude at the same time; the IDE save overwrote Claude's edits once. Re-read before editing.
