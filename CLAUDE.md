# CLAUDE.md

Zidong's personal website, served at https://zidongzhao.github.io. **Public**: everything in this repo is readable by anyone, so no secrets, no phone number, no plain email address. See `SPEC.md` for the design; `SOURCES.md` (gitignored) holds resume and LinkedIn text for copy.

## Stack and commands

- Plain HTML, CSS, vanilla JS. No framework, no build step.
- Run locally: `uv run python -m http.server 8000`, then open http://localhost:8000
- Check: `uv run tests/check_site.py`; browser checks: `uv run tests/browser_check.py http://127.0.0.1:8000 /tmp/shots` (first time: `uv run --with playwright playwright install chromium webkit`). WebKit stands in for iOS Safari; it is close, not exact.
- Test on a phone: `uv run python -m http.server 8000 --bind 0.0.0.0`, open `http://<Mac's Wi-Fi address>:8000` on a phone on the same Wi-Fi, stop the server afterward. Trusted home network only.
- Deploy: merge into `master` and push; GitHub Pages publishes it. Ask Zidong first. Afterward, rerun the browser checks against https://zidongzhao.github.io.
- Share image: `uv run scripts/share_card.py` rebuilds `assets/share-card.jpg` (link preview). Rerun after changing the name, 赵紫东, the focus line, the photo, or the colors; `check_site.py` fails until you do, and the pre-commit hook in `.githooks/` runs it. On a fresh clone, enable the hook with `git config core.hooksPath .githooks`. After deploying a new card, re-inspect the URL in LinkedIn Post Inspector so LinkedIn drops its cached preview.
- History of the October 2026 revamp, checks, and open items: `docs/2026-10-19-revamp-record.md`.

## Decisions

- Plain HTML over Astro: one page that changes a few times a year. Move to Astro only if projects grow into many pages.
- Jekyll stays on (GitHub Pages default) only so `_config.yml` can exclude project docs from the live site.
- `old-site/` is the full pre-2026 site, kept for reference. Its pages carry `noindex` and `robots.txt` disallows it. Nothing on the new site links into it. Its root-relative links are broken by design.
- Old top-level URLs redirect to sections of the new page.

## Gotchas

- SPEC.md has been edited in the IDE and by Claude at the same time; the IDE save overwrote Claude's edits once. Re-read before editing.
- Phone vs. sidebar layout is decided by two complementary media queries, `(max-width: 699.98px), (max-height: 499.98px)` and `(min-width: 700px) and (min-height: 500px)`, used for layout and type sizes alike. Change them together; the .98 keeps fractional viewports from matching neither.
- The sticky phone Menu bar depends on `--bar-hide` and `--bar-h`, measured in `js/site.js`. Without JS the header just scrolls away.
- Zidong tests on Android only; iOS is covered by Playwright WebKit alone.
