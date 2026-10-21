# Site revamp record (October 2026)

What changed on zidongzhao.github.io, why, how it was checked, and what's still open. Design detail lives in `SPEC.md`; the task-by-task build plan is `docs/superpowers/plans/2026-10-19-site-revamp.md`.

**Status:** built, reviewed, and committed on branch `revamp` (9 commits on top of `6c071ba`). Not deployed; deploy waits on Zidong's go-ahead.

## Why

The old site presented Zidong as a Yale research scientist with a fully academic framing: six pages (About, Research, Publications, CV, Collaborators, Contact), an empty CV page, and a leftover "twitter widget" placeholder. Zidong is now a senior quantitative UX researcher looking for UX research and product data science roles. The new site is one page for hiring managers, recruiters, and peers in research, insights, and product, and it complements LinkedIn rather than repeating it.

## What the site is now

A single scrolling page with a pinned sidebar on desktop and a top header on phones.

**Sidebar:** name in Newsreader serif, 赵紫东, "Quantitative UX Researcher", the focus line "UX Research · Product Data Science · Behavioral Insights", section links that highlight as you scroll, and LinkedIn, GitHub, and Google Scholar icons.

**Sections, in order:**

| Section | Contents |
|---|---|
| About | Headshot, the positioning line ("Bridging human behavior and complex technical systems, turning experience into measurable signals and product decisions."), and three short paragraphs: Instagram, Yale and Princeton, toolkit |
| Experience | Cards for Instagram, HelloNova (linked to thenovaland.com), Yale (Laurie Santos linked), Princeton |
| Projects | UX research portfolio card with a disabled "Coming soon" button; five academic publications with PDF and DOI links |
| Resume | Download button and an inline PDF viewer that falls back to a download link where browsers can't show PDFs |
| Academics | "In a previous life..." opener, Princeton and Vanderbilt paragraphs, collaborator links |
| Contact | Email written as "at ... dot com" text with no mailto link, plus profile links |

**Look:** light sage background (`#eef6f0`), forest green highlights (`#3d7a48`), pink decorations, and a matching dark mode (deep pine, mint, dusty rose) that follows the visitor's system setting. Newsreader is used only for the name and positioning line; IBM Plex Sans for everything else.

**Interactions:** pink highlight sweeps across text links, social icons tilt and grow, experience cards tilt toward the cursor. All of them respond to keyboard focus where it applies, switch off under "reduce motion", and card tilt skips touch screens.

## How it got here

1. **Interview and mockups.** Positioning, audience, and sections were worked out in conversation. Visual choices were made from side-by-side mockups in a local browser tab: layout (one page with sidebar), palette (original green and pink, with light sage as background), animations, dark mode, and fonts (Newsreader with IBM Plex Sans, compared at matched lowercase height).
2. **Spec.** `SPEC.md` was written, read by a reviewer posing as the builder, and revised with Zidong's answers. Zidong edited it directly as well (audience, contact flow, Academics opener). One IDE save overwrote two spec edits; they were restored.
3. **Positioning.** Recommendation systems were dropped as the brand in favor of Zidong's line about bridging human behavior and technical systems. The sidebar line went through three versions (a short tagline, a skills list, then the current high-level focus line) to serve both UX research and product data science roles without listing tools.
4. **Plan and build.** Six tasks, each test-first: write failing checks, build until they pass, commit. Copy was reviewed and approved by Zidong mid-build.
5. **Final review.** A fresh reviewer read the whole branch. Its Important findings were fixed test-first in one pass (see Final review below).

## Commits on `revamp`

| Commit | What |
|---|---|
| `77e026b` | Move old site into `old-site/`; add noindex, robots.txt, `_config.yml` exclusions, check script, CLAUDE.md, README |
| `6db2765` | Page skeleton, color tokens with dark mode, type system |
| `d39c664` | Remove a personal image from the archive |
| `f8228d9` | About, Experience, Academics, Contact copy; headshot |
| `4c1fdc1` | Projects and Resume sections |
| `1df2768` | Hover effects, card tilt, phone menu, active nav, social icons |
| `dbdaa8f` | Redirects for 13 old URLs; sitemap now lists only the home page |
| `d8944b2` | Fixes from browser screenshots: sidebar wrapping, phone spacing, PDF fallback |
| `6777bde` | Fixes from final review: Contact nav highlight, menu fallback if `site.js` fails, papers back at their old `/files/` URLs |

## Files

| Path | Role |
|---|---|
| `index.html` | The whole page |
| `css/site.css` | Tokens, type scale, layout, interactions |
| `js/site.js` | Phone menu, active nav highlight, card tilt |
| `assets/` | Headshot, resume PDF, favicons |
| `files/` | The five publication PDFs, at the same URLs as on the old site |
| `cv.html`, `publications.html`, `research.html`, `collaborators.html`, `contact.html`, `publications/*.html` | Redirect pages to the matching section |
| `robots.txt`, `sitemap.xml`, `_config.yml`, `google60a4458eb7076ec4.html` | Crawling rules, Pages config, Search Console verification |
| `old-site/` | The entire previous site, kept for reference |
| `tests/check_site.py`, `tests/browser_check.py` | Automated checks |
| `SPEC.md`, `CLAUDE.md`, `README.md`, `docs/` | Project docs (excluded from the live site) |

## The archive

Every tracked file of the old site moved into `old-site/` with `git mv`, so history follows each file. Each archived HTML page got one added line, `<meta name="robots" content="noindex">`, and `robots.txt` disallows `/old-site/`. Nothing on the new site links into it. Its internal links point to the site root, so it's a reference copy, not a working mirror.

One deviation from "unchanged": a personal image (two copies) was deleted at Zidong's request. History cleanup is tracked under Open items.

The archive still holds an old CV PDF and an old resume PDF that contain contact details. Zidong chose to keep them, given the folder isn't indexed. They remain readable to anyone browsing the public repo.

## Privacy measures

- No usable email address and no phone number in any served file outside `old-site/`. The check script scans every served text file for both.
- The resume PDF is a phone-free export. The check script reads its text with `pypdf` to confirm. It keeps the email address, since recruiters expect it there.
- The headshot was re-encoded with no EXIF metadata (location, device). The check script verifies this.
- `SOURCES.md` (resume and LinkedIn text used for copy) is gitignored.
- `_config.yml` excludes SPEC.md, SOURCES.md, CLAUDE.md, README.md, `docs/`, and `tests/` from the live site.

## Verification

**Static checks:** `uv run tests/check_site.py` → **137/137 passed**. They cover the archive and noindex rules, config exclusions, no em dashes, page structure and nav order, font loading and fallbacks, WCAG AA contrast for every text color in both modes, analytics tag, copy rules (positioning line verbatim, experience order, Academics opener, no posters), email and phone scans, photo size and metadata, publications and DOIs, resume viewer and fallback, interaction and accessibility rules, redirects, old PDF URLs, sitemap, and broken or archive-bound links.

**Browser checks:** `uv run tests/browser_check.py http://127.0.0.1:8000 <dir>` with Playwright's Chromium → **42/42 passed**. They cover no horizontal scroll and no console errors at 1280, 375, and 320px in light and dark mode; fonts loading; nav click scrolling and active highlight, including the last section; card tilt, icon tilt, and link sweep; reduced motion stopping movement; the phone menu opening, closing, and staying visible without JavaScript or when `site.js` fails to load; three old URLs landing on the right sections; all five DOIs resolving; all papers and the resume being served.

Screenshots were reviewed by eye. They caught three issues the automated checks missed (sidebar phrase breaking mid-item, phone menu touching the icons, a blank PDF viewer), all fixed in `d8944b2`.

**Not verified:**
- Inline PDF rendering in a real desktop browser. Headless Chromium has no PDF viewer, so only the fallback was seen.
- Real iOS Safari and Android devices.
- The live site. After deploy, rerun both checks against https://zidongzhao.github.io and confirm SPEC.md and SOURCES.md return 404.

## Final review

A fresh reviewer (most capable model) read the whole branch against the spec and the plan's Review Focus list, and probed the running site with Playwright.

**Passed:** no horizontal scroll at 320, 375, and 1280px; readable page with Google Fonts blocked (about 27px of total height shift); phone menu usable with JavaScript off; skip link, logical tab order, and visible focus for keyboard users; old HTML URLs landing on the right sections; no email address in served files; nothing private served by Jekyll.

**Critical:** none.

**Important, all fixed in `6777bde` with tests that failed first:**
1. Contact never highlighted in the nav, because the short last section couldn't reach the highlight band.
2. If `site.js` failed to load, phones got a Menu button that did nothing. The script tag now restores the open menu on load failure.
3. Old paper PDF URLs (`/files/*.pdf`) returned 404. The papers now live at those URLs again; the old CV PDF was not republished.
4. A file deleted from the archive is still in git history (see Open items). This needs Zidong's decision, not code.

**Deferred minors** (not fixed; candidates for later polish):
- Light-mode link hover state is 4.25:1 contrast (forest green on the pink sweep); AA asks for 4.5.
- Sidebar nav and button hover styles have no keyboard-focus counterpart (the focus outline still shows).
- The global focus style changes a button's corner radius from 8px to 4px.
- The no-horizontal-scroll check doesn't test long unbreakable strings added later.
- The post-deploy "not served" check should also cover `/docs/` and `/README.md`.
- Two published paper PDFs include an old Princeton office address (standard corresponding-author lines).
- Serif text shifts slightly when Newsreader finishes loading.

## Decisions made during the build

| Decision | Why | Cost if wrong |
|---|---|---|
| Worked on branch `revamp` in place, no separate worktree | Fresh clone, nothing else in flight | None |
| Dark-mode muted text lightened from `#7d8c82` to `#87968c` | Failed WCAG AA on cards (4.21:1) | Slightly lighter dates in dark mode |
| Sidebar tagline replaced by a focus line | Zidong's request; serves UXR and product DS roles | None |
| Laurie Santos linked in the Yale card, not Academics | Zidong confirmed | None |
| Personal image deleted from archive | Zidong approved | None; history cleanup is a separate decision |
| Headshot cropped with a one-off Pillow script outside the project | macOS `sips` ignored crop offsets; Pillow also strips metadata | Re-crop |
| Portfolio card copy kept generic | Portfolio contents unknown | One line of copy |
| `.js` class set in an inline head script as well as in `site.js` | Prevents the phone menu flashing open before the script runs | One inline line |
| Browser checks run with Playwright | Claude in Chrome extension never connected; Zidong chose Playwright | None |
| Resume viewer switched from `<embed>` to `<object>` with a download fallback | Android Chrome and headless browsers can't show inline PDFs | None |
| Papers moved from `assets/papers/` back to `files/` | Scholar and old CVs link to those PDF URLs; GitHub Pages can't redirect PDFs | None |
| Last section given `min-height: 75vh` | Lets Contact reach the active-nav band; a bottom-of-page JS rule was tried first and wrongly highlighted Contact after clicking Academics | Some empty space below Contact |

## Open items

- **Deploy:** merge `revamp` into `master` and push, then rerun the checks on the live site. Needs Zidong's go-ahead.
- **Git history:** decide whether to purge the file removed in `d39c664` from history. That needs a history rewrite and force-push.
- **Later list (from SPEC.md):** page motion (sliding nav highlight, fade-up sections), the real portfolio URL in place of "Coming soon", personal projects, and moving to Astro only if projects grow into many pages.
- **Next session (2026-10-21):** rework all copy substantially, and do a full mobile pass (real iOS Safari and Android, plus Safari rendering of the speck texture, are still untested).

## How to run and update

- Preview: `uv run python -m http.server 8000`, open http://localhost:8000
- Checks: `uv run tests/check_site.py`; browser checks need `uv run --with playwright playwright install chromium` once.
- Deploy: merge into `master` and push; GitHub Pages publishes within a few minutes.
