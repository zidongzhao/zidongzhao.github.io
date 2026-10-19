# zidongzhao.github.io Revamp Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the academic multi-page site at zidongzhao.github.io with a single-page professional site, keeping the old site as an unindexed archive in `old-site/`.

**Architecture:** One `index.html`, one stylesheet, one small JS file, served as-is by GitHub Pages from the existing repo. Old site files move under `old-site/` with `git mv` so history is preserved. A stdlib Python check script (`tests/check_site.py`, run through uv) pins every testable spec rule; visual behavior is verified by browser screenshots.

**Tech Stack:** HTML, CSS (custom properties, `prefers-color-scheme`, `prefers-reduced-motion`), vanilla JS, Google Fonts (Newsreader, IBM Plex Sans, Noto Serif SC), GitHub Pages (Jekyll left on, used only for `exclude`).

**Spec:** `SPEC.md` (read it first). Source text for copy: `SOURCES.md` (gitignored).

## Global Constraints

- No framework, no build step, no package manager. Python only via `uv run`; the check script uses the standard library except Task 4's PDF check (`pypdf`, inline script dependency).
- No em dashes (—) and no spaced hyphens standing in for them, in any HTML, CSS, JS, README, or commit message.
- No email address in usable form in any served file outside `old-site/`. Contact text is exactly `zhaozidong1993 at gmail dot com`. No `mailto:`.
- No phone number anywhere outside `old-site/`, including the new resume PDF.
- Positioning line, verbatim: `Bridging human behavior and complex technical systems, turning experience into measurable signals and product decisions.`
- Sidebar tagline (working version): `Making human experience measurable.`
- Section order and ids: `about`, `experience`, `projects`, `resume`, `academics`, `contact`.
- Nothing on the new site links into `old-site/`.
- Copy uses only facts from `SOURCES.md` and the old site. Zidong approves all copy before deploy.
- Deploying (push to `master`) needs Zidong's explicit yes.

## Review Focus

1. **Phones at 320 to 375px with long unbreakable strings** (DOIs, the email text, "Quantitative"): a visitor expects no horizontal scroll. Pinned by `overflow-wrap:anywhere` on body text and the 320px screenshot in Task 6.
2. **Google Fonts blocked or slow** (corporate networks, mainland China): a visitor expects a readable page in Georgia/system fonts with no layout jump. Pinned by the fallback-stack assertion in Task 2.
3. **JavaScript disabled or failed:** a visitor on a phone still expects to reach every section. The mobile menu is open by default and only collapses after JS adds `class="js"` to `<html>`. Pinned in Task 5.
4. **Keyboard-only visitor:** expects a skip link, visible focus, and the same hover effects on focus. Pinned by the skip-link and `:focus-visible` assertions in Task 5.
5. **Old inbound links** from Scholar or old CVs (`/publications/ZhaoSenedTamir2023.html`, `/cv.html`): visitors expect to land on the right section, not a 404. Pinned in Task 6.

---

## File structure (repo root = `website/`)

| Path | Responsibility |
|---|---|
| `index.html` | The whole page: sidebar, six sections, GA tag, font links |
| `css/site.css` | Tokens (light/dark), type scale, layout, interactions |
| `js/site.js` | Adds `js` class, mobile menu, active nav highlight, card tilt |
| `assets/papers/*.pdf` | Publication PDFs copied from the old site |
| `assets/Zidong-Zhao-Resume.pdf` | Resume, supplied by Zidong |
| `assets/favicon-16x16.png`, `assets/favicon-32x32.png`, `favicon.ico` | Copied from old site |
| `cv.html`, `publications.html`, `research.html`, `collaborators.html`, `contact.html`, `publications/*.html` | Redirect stubs |
| `robots.txt`, `sitemap.xml`, `_config.yml`, `google60a4458eb7076ec4.html` | Crawling and Pages config |
| `old-site/` | Entire old site, moved unchanged except an added `noindex` meta in each HTML page |
| `tests/check_site.py` | All automated checks |
| `CLAUDE.md`, `README.md`, `SPEC.md`, `.gitignore` | Project docs |

---

### Task 1: Repo setup and archive

**Files:**
- Create: `.gitignore`, `_config.yml`, `robots.txt`, `CLAUDE.md`, `tests/check_site.py`
- Modify: `README.md`, every `old-site/**/*.html` (add one meta tag)
- Move: every tracked file of the old repo into `old-site/`

**Interfaces:**
- Produces: `tests/check_site.py` with `check(name: str, ok: bool, detail: str = "")` that records results, one `def test_<area>()` function per area, and `main()` that runs all `test_*` functions and exits 1 on any failure. Later tasks add `test_*` functions. Helpers: `served_files() -> list[Path]` (all files outside `old-site/`, `tests/`, `docs/`, `.git/`, `.superpowers/`, and the `_config.yml` exclude list), `read(path) -> str`.

- [ ] **Step 1: Turn `website/` into a clone of the existing repo without disturbing SPEC.md, SOURCES.md, .superpowers**

```bash
cd ~/projects/vibe/website
git init -b master && git remote add origin https://github.com/zidongzhao/zidongzhao.github.io.git
git fetch origin && git checkout -t origin/master
git checkout -b revamp
```
Expected: `git log --oneline | head -1` shows `6c071ba one more try at fixing the color`.

- [ ] **Step 2: Write `tests/check_site.py` with `test_archive()` and `test_repo_hygiene()`**

`test_archive` asserts: `old-site/index.html`, `old-site/research.html`, `old-site/files/CV_Zidong Zhao_041621.pdf`, `old-site/backup_20250322_112858/index.html`, `old-site/Resume_Zidong Zhao_ds1p.pdf` exist; every `old-site/**/*.html` except `google60a4458eb7076ec4.html` contains `<meta name="robots" content="noindex">`; `robots.txt` contains the line `Disallow: /old-site/`.
`test_repo_hygiene` asserts: `.gitignore` lists `SOURCES.md` and `.superpowers/`; `_config.yml` `exclude` lists `SPEC.md`, `SOURCES.md`, `CLAUDE.md`, `README.md`, `docs`, `tests`; `google60a4458eb7076ec4.html` exists at root; no served file contains `—`.

- [ ] **Step 3: Run it, expect failures**

Run: `uv run tests/check_site.py`
Expected: FAIL on archive and hygiene checks.

- [ ] **Step 4: Move the old site and add config**

`git mv` every tracked top-level entry into `old-site/` (keep `README.md` at root). Copy `old-site/google60a4458eb7076ec4.html` back to root. Insert `<meta name="robots" content="noindex">` right after each `<head>` tag in `old-site/**/*.html` (skip the Google verification file). Write `robots.txt` (`User-agent: *`, `Disallow: /old-site/`, `Sitemap: https://zidongzhao.github.io/sitemap.xml`), `_config.yml` with the exclude list, `.gitignore` (`SOURCES.md`, `.superpowers/`, `.DS_Store`). Write `CLAUDE.md` per the vibe rules: what it is (public), stack, run command `uv run python -m http.server 8000`, test command `uv run tests/check_site.py`, deploy = merge to `master`, decisions (plain HTML; Jekyll kept only for `exclude`; old-site archive), gotcha (reload SPEC.md in the IDE before editing; conflicts happened). Update `README.md`: what it is, how to run and check.

- [ ] **Step 5: Run checks, expect pass**

Run: `uv run tests/check_site.py`
Expected: all archive and hygiene checks PASS.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "Move old site into old-site/ and add check script"
```

---

### Task 2: Page skeleton, tokens, and type

**Files:**
- Create: `index.html`, `css/site.css`, `assets/favicon-16x16.png`, `assets/favicon-32x32.png`, `favicon.ico` (copied from `old-site/images/`)
- Test: `tests/check_site.py` (add `test_structure`, `test_fonts`, `test_contrast`, `test_analytics`)

**Interfaces:**
- Produces: section ids from Global Constraints; sidebar `<nav id="site-nav">` with `<a href="#about">` and so on, in order; `<button id="nav-toggle" aria-controls="site-nav" aria-expanded="false">`; skip link `<a class="skip" href="#main">`; `<main id="main">`. CSS custom properties on `:root`, redefined under `@media (prefers-color-scheme: dark)`: `--bg --card --card-border --ink --body --muted --accent --pink-divider --pink-border --pink-edge --pink-soft`. Class names used by later tasks: `.card` (experience and project cards), `.social` (icon links), `.prose a` (text links that get the sweep), `.btn` (buttons).

- [ ] **Step 1: Add tests**

`test_structure`: `index.html` has `<html lang="en">`, a `<title>` of `Zidong Zhao`, a meta description, the six `<section id=...>` in order, nav hrefs equal `#` + those ids in the same order, the skip link, and the toggle button with both aria attributes.
`test_fonts`: one Google Fonts css2 link containing `Newsreader`, `IBM+Plex+Sans`, `display=swap`; a separate link for `Noto+Serif+SC` whose `text=` parameter decodes to `赵紫东`; `site.css` contains `Georgia` in the serif stack, `system-ui` in the sans stack, and `font-size-adjust`.
`test_contrast`: parse the light and dark token blocks from `site.css`; WCAG ratio ≥ 4.5 for each of `--ink`, `--body`, `--muted`, `--accent` against both `--bg` and `--card`, in each mode. Implement the WCAG relative-luminance formula in the script.
`test_analytics`: `index.html` contains `G-L9Q1GGPFNJ`.

- [ ] **Step 2: Run, expect FAIL** (`uv run tests/check_site.py`)

- [ ] **Step 3: Build the skeleton**

Token values, light and dark, and the type table come from SPEC.md "Visual system" verbatim. If `test_contrast` fails for a pair, darken (light mode) or lighten (dark mode) that token, keeping its hue, until it passes. Layout: at ≥ 900px a sticky sidebar column (about 300px, right border 6px `--pink-divider`) and a content column with max width about 70ch; below 900px the sidebar becomes a top header. Section headings are the uppercase Plex labels from the type table. Sections are empty shells with their label in this task. Sidebar holds name, 赵紫东 in `lang="zh"`, `Quantitative UX Researcher`, the tagline, nav, and an empty `.social` row.

- [ ] **Step 4: Run, expect PASS**

- [ ] **Step 5: Commit** `git commit -am "Add page skeleton, color tokens, and type system"` (add new files first)

---

### Task 3: Copy for About, Experience, Academics, Contact

**Files:**
- Modify: `index.html`
- Test: `tests/check_site.py` (add `test_copy`)

**Interfaces:**
- Consumes: section ids, `.card`, `.prose a` from Task 2.

- [ ] **Step 1: Add `test_copy`**

Asserts: `#about` contains the positioning line verbatim; no served file matches `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}` or `mailto:`; `#contact` contains `zhaozidong1993 at gmail dot com`; no served file matches a US phone pattern `\(?\d{3}\)?[ .-]?\d{3}[ .-]?\d{4}`; `#experience` has exactly 4 `.card` elements in order Instagram, HelloNova, Yale, Princeton; `#academics` starts with a paragraph containing `In a previous life`; `#academics` contains no `poster`; the sidebar tagline does not contain `recommendation`.

- [ ] **Step 2: Run, expect FAIL**

- [ ] **Step 3: Write the copy**

Follow SPEC.md "Page structure" items 1, 2, 5, 6 and SOURCES.md. Experience cards: role, org, dates in the Meta style, two or three lines in a voice that complements LinkedIn (outcomes and how, not bullet copies). Instagram in past tense. Academics: the opener (Zidong's wording, tightened only if needed), one paragraph each for Princeton and Vanderbilt condensed from `old-site/research.html` and `old-site/index.html`, then one line of collaborator names with their old links, mentors linked (Laurie Santos links to `https://www.drlauriesantos.com/`). Contact: the email text plus LinkedIn, GitHub, Scholar links from SPEC.md "Sources". All copy obeys the writing rules in `~/.claude/CLAUDE.md` (no em dashes, no contrastive negation, plain verbs).

- [ ] **Step 4: Run, expect PASS**

- [ ] **Step 5: Copy review gate.** Show Zidong the rendered copy (Task 6 server plus screenshot, or the text) and apply their edits. Do not continue until they approve.

- [ ] **Step 6: Commit** `"Write About, Experience, Academics, and Contact copy"`

---

### Task 4: Projects and Resume

**Prerequisite:** Zidong has placed the phone-free resume PDF at `assets/Zidong-Zhao-Resume.pdf`. Ask for it at the start of this task if missing.

**Files:**
- Create: `assets/papers/{ZhaoSenedTamir2023,ZhaoThorntonTamir2020,BBS2020_PredictiveSubstrate,MeyerZhaoTamir2019,OlatunjiBergZhao2017}.pdf` (copied from `old-site/files/`)
- Modify: `index.html`
- Test: `tests/check_site.py` (add `test_projects`, `test_resume`)

- [ ] **Step 1: Add tests**

`test_projects`: `#projects` contains a portfolio `.card` whose action is a `<button disabled>` (or `aria-disabled="true"` element) with text `Coming soon` and no `href`; exactly 5 publication entries, each with one PDF link to an existing file under `assets/papers/` and one DOI link; the five DOIs from SPEC.md all appear as `https://doi.org/<doi>`; the BBS PDF link ends in `#page=52`, the Thornton link in `#page=2`; journal names are in `<i>` or `<em>`.
`test_resume`: `#resume` has an `<embed>` (or `<object>`) whose `src` is `assets/Zidong-Zhao-Resume.pdf`, and an `<a class="btn" download>` to the same file that comes before the embed in source order; the PDF exists; extracted PDF text (via `pypdf`) has no phone-pattern match. `pypdf` goes in the script's inline `# /// script` dependencies.

- [ ] **Step 2: Run, expect FAIL**

- [ ] **Step 3: Build both sections**

Publications in the old site's citation format, with Zidong's name in bold. Resume: one summary line, the download button, then the embed at about 80vh on desktop. Below 900px, hide the embed's fixed height and keep the button first (the source order already does this).

- [ ] **Step 4: Run, expect PASS**

- [ ] **Step 5: Commit** `"Add Projects and Resume sections"`

---

### Task 5: Interactions, icons, and accessibility

**Files:**
- Create: `js/site.js`
- Modify: `index.html` (inline SVG icons, script tag with `defer`), `css/site.css`
- Test: `tests/check_site.py` (add `test_interactions`)

**Interfaces:**
- Consumes: `#nav-toggle`, `#site-nav`, `.card`, `.social`, `.prose a`, `.btn` from Task 2.
- Produces in `js/site.js`: `initMenu()`, `initActiveNav()`, `initTilt()`, called on load after `document.documentElement.classList.add('js')`.

- [ ] **Step 1: Add `test_interactions`**

Asserts in `site.css`: a `@media (prefers-reduced-motion: reduce)` block exists and sets `transition` and `transform` to none for `.card`, `.social a`, `.prose a`; `:focus-visible` styles exist; the mobile menu's collapsed rule is scoped under `.js` (search for `.js` in the selector that hides `#site-nav`); `.social` icons are inline `<svg>` with `aria-hidden="true"` inside links that have `aria-label`. In `site.js`: `matchMedia('(pointer: fine)')` and `prefers-reduced-motion` both gate `initTilt`; `aria-expanded` is toggled.

- [ ] **Step 2: Run, expect FAIL**

- [ ] **Step 3: Implement**

Effects as decided in SPEC.md "Interactions": link sweep is a `--pink-soft` background-size transition from 0% to 100% on hover and `:focus-visible`; icon tilt is `rotate(-10deg) scale(1.12)` with `--pink-soft` fill; card tilt follows the pointer at up to 5deg per axis with `perspective(600px)` and resets on leave. Active nav uses `IntersectionObserver` to mark the visible section's link with `aria-current="true"`, styled with `--pink-soft`. Mobile menu closes on link click and on Escape.

- [ ] **Step 4: Run, expect PASS**

- [ ] **Step 5: Commit** `"Add hover effects, card tilt, mobile menu, and active nav"`

---

### Task 6: Redirects, sitemap, and full verification

**Files:**
- Create: `cv.html`, `publications.html`, `research.html`, `collaborators.html`, `contact.html`, `publications/{ZhaoSenedTamir2023,ZhaoThorntonTamir2020,ZhaoMildnerTamir2020,MeyerZhaoTamir2019,OlatunjiBergZhao2017,sans2019,spsp2018,spsp2019}.html`
- Modify: `sitemap.xml`
- Test: `tests/check_site.py` (add `test_redirects`, `test_links`)

- [ ] **Step 1: Add tests**

`test_redirects`: each stub has `<meta http-equiv="refresh" content="0; url=/#<id>">`, `<link rel="canonical">` to the same URL, `noindex`, and a visible fallback link. Targets: `cv.html` → `resume`; `publications.html` and every `publications/*.html` → `projects`; `research.html`, `collaborators.html` → `academics`; `contact.html` → `contact`. `sitemap.xml` lists only `https://zidongzhao.github.io/`.
`test_links`: every local `href`/`src` in served HTML resolves to an existing file (strip `#...`); no served HTML links into `old-site/`.

- [ ] **Step 2: Run, expect FAIL**, then **Step 3: create stubs and sitemap**, then **Step 4: run, expect all checks PASS**

- [ ] **Step 5: Browser check.** Serve with `uv run python -m http.server 8000` and open `http://localhost:8000` in Chrome (Claude in Chrome). Screenshot at 1280px and 320px, light and dark. Confirm: no horizontal scroll at 320px; sidebar links scroll to sections; the resume embed renders and the download returns the file; the three hover effects work; with reduced motion emulated, they don't move; with JS disabled, the phone menu is visible; `/cv.html` and `/publications/ZhaoSenedTamir2023.html` land on the right sections; DOI links open the papers. If the Chrome extension doesn't respond, stop and ask Zidong (Playwright would be a new dependency).

- [ ] **Step 6: Commit** `"Add redirects for old URLs and update sitemap"`

- [ ] **Step 7: Whole-branch review** in a fresh context (`/code-review` or a review subagent). Fix gaps in correctness, privacy, or the spec; list the rest.

- [ ] **Step 8: Deploy, only after Zidong's yes.** Merge `revamp` into `master` and push. Wait for Pages to build, then repeat the Step 5 checks on `https://zidongzhao.github.io`. Confirm `https://zidongzhao.github.io/SPEC.md` and `/SOURCES.md` return 404.
