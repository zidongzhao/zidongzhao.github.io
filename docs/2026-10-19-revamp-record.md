# Site revamp record (October 2026)

What changed on zidongzhao.github.io, why, how it was checked, and what's still open. Design detail lives in `SPEC.md`; the task-by-task plan for the first build is `docs/superpowers/plans/2026-10-19-site-revamp.md`.

**Status:** live. Built October 19 to 20, deployed October 20 (site code as of `eebb0ab`; later commits touch docs only), and checked against the live site the same day. The work is closed; what remains is under Open items.

## Why

The old site presented Zidong as a Yale research scientist with a fully academic framing: six pages (About, Research, Publications, CV, Collaborators, Contact), an empty CV page, and a leftover "twitter widget" placeholder. Zidong is now a senior quantitative UX researcher looking for UX research and product data science roles. The new site is one page for hiring managers, recruiters, and peers in research, insights, and product, and it complements LinkedIn rather than repeating it.

## What the site is now

A single scrolling page. Desktop has a pinned sidebar; phones (under 700px wide, or under 500px tall) get a top header whose Menu row stays pinned as a slim bar.

**Sidebar:** name in Newsreader serif, 赵紫东 in Long Cang, the focus line "UX Research · Product Data Science · Behavioral Insights" (no job title line), section links that highlight as you scroll, LinkedIn, GitHub, and Google Scholar icons, and a light/dark switch.

**Sections, in order:**

| Section | Contents |
|---|---|
| About | Headshot, the positioning line ("I study how people interact with complex technology, and turn what I learn into metrics and product decisions."), and three short paragraphs: Instagram, Yale and Princeton, toolkit |
| Experience | Cards for Instagram, HelloNova (NovaLand linked in the body text), Yale (Laurie Santos linked), Princeton |
| Projects | UX research portfolio card with a disabled "Coming soon" button |
| Resume | A download button only |
| Academics | "In a previous life..." opener, Princeton and Vanderbilt paragraphs, then two collapsed dropdowns: "Read more about my academic work" (three research themes with collaborators linked) and "Academic publications" (five papers with PDF and DOI links) |
| Contact | Email written as "at ... dot com" text with no mailto link, plus profile links |

**Look:** light sage background (`#eef6f0`) with a recycled-paper fleck texture, forest green highlights (`#3d7a48`), pink decorations, cards with a 1.5px ink outline and an offset pink shadow, and a matching dark mode (deep pine, mint, dusty rose). Dark mode follows the system setting until the visitor picks one with the switch; the choice is remembered. Newsreader is used only for the name and positioning line; IBM Plex Sans for everything else.

**Interactions:** pink highlight sweeps across text links, social icons tilt and grow, experience and portfolio cards tilt toward the cursor, section labels pin while their section is on screen, and the dropdowns open with a +/× toggle. Effects respond to keyboard focus where it applies and switch off under "reduce motion". Hover effects apply only to a mouse or trackpad, and every control is at least 44px to tap.

## How it got here

1. **Interview and mockups (Oct 19).** Positioning, audience, and sections were worked out in conversation. Visual choices were made from side-by-side mockups: layout, palette, animations, dark mode, and fonts.
2. **Spec.** `SPEC.md` was written, read by a reviewer posing as the builder, and revised with Zidong's answers. Zidong edited it directly as well. One IDE save overwrote two spec edits; they were restored.
3. **Plan and build.** Six tasks, each test-first: write failing checks, build until they pass, commit.
4. **Final review.** A fresh reviewer read the whole branch. Its Important findings were fixed test-first in one pass (see Final review below).
5. **Visual polish (Oct 19 to 20).** From Zidong's feedback in the browser: a larger Chinese name in Long Cang, layouts for wide, tablet, and phone widths, softer card tilt, a download-only Resume section, pinned section labels, the paper texture, the light/dark switch, restyled cards, and publications folded into a dropdown.
6. **Copy rework (Oct 20).** The job title left the sidebar and search snippet. About, the Instagram, HelloNova, and Yale cards were rewritten, and the old research themes were folded into Academics as a second dropdown.
7. **Mobile pass (Oct 20).** A sticky Menu bar (Zidong's pick), 44px tap targets, hover effects limited to mouse and trackpad, phone layout for landscape phones, and phone-profile browser checks. Zidong confirmed a 9-item checklist on an Android phone over home Wi-Fi. A code review of the pass found ten issues; six were fixed (see Mobile review).
8. **Publications move (Oct 20).** "Academic publications" moved from Projects into Academics, after "Read more", with the stacked dropdowns spaced as one list. Old publication URLs now redirect to Academics.
9. **Deploy (Oct 20).** `revamp` was fast-forwarded into `master` and pushed (`6c071ba..eebb0ab`), with no force-push.

## Commits

All on `revamp`, fast-forwarded into `master`.

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
| `e5ab239`, `470a96b` | This record; reworded archive check |
| `fbb45bb` to `0929f9c` | Visual polish: Chinese name, responsive widths, card tilt, download-only Resume, pinned labels, texture, theme switch, card style |
| `be5f343`, `b01e9aa` | Publications in a collapsed dropdown with a +/× toggle |
| `cdff100` | Next-session plan in this record |
| `953bc8c` to `36f7429` | Copy rework: sidebar title, About, Experience cards, research themes into Academics |
| `410540a`, `8ae8059`, `6442791` | Mobile pass, its spec update, and fixes from its review |
| `0802620` | Publications moved into Academics |
| `eebb0ab` | Commit IDs in this record updated |

## Files

| Path | Role |
|---|---|
| `index.html` | The whole page |
| `css/site.css` | Tokens, texture, type scale, layout, interactions |
| `js/site.js` | Phone menu, sticky phone bar measurements, active nav highlight, card tilt, theme switch |
| `assets/` | Headshot, resume PDF, favicons |
| `files/` | The five publication PDFs, at the same URLs as on the old site |
| `cv.html`, `publications.html`, `research.html`, `collaborators.html`, `contact.html`, `publications/*.html` | Redirect pages to the matching section |
| `robots.txt`, `sitemap.xml`, `_config.yml`, `google60a4458eb7076ec4.html` | Crawling rules, Pages config, Search Console verification |
| `old-site/` | The entire previous site, kept for reference |
| `tests/check_site.py`, `tests/browser_check.py` | Automated checks |
| `SPEC.md`, `CLAUDE.md`, `README.md`, `docs/` | Project docs (excluded from the live site) |

## The archive

Every tracked file of the old site moved into `old-site/` with `git mv`, so history follows each file. Each archived HTML page got one added line, `<meta name="robots" content="noindex">`, and `robots.txt` disallows `/old-site/`. Nothing on the new site links into it. Its internal links point to the site root, so it's a reference copy, not a working mirror.

One deviation from "unchanged": a personal image (two copies) was deleted at Zidong's request.

The archive still holds an old CV PDF and an old resume PDF that contain contact details. Zidong chose to keep them, given the folder isn't indexed. They remain readable to anyone browsing the public repo.

## Privacy measures

- No usable email address and no phone number in any served file outside `old-site/`. The check script scans every served text file for both.
- The resume PDF is a phone-free export. The check script reads its text with `pypdf` to confirm. It keeps the email address, since recruiters expect it there.
- The headshot was re-encoded with no EXIF metadata (location, device). The check script verifies this.
- `SOURCES.md` (resume and LinkedIn text used for copy) is gitignored.
- `_config.yml` excludes SPEC.md, SOURCES.md, CLAUDE.md, README.md, `docs/`, and `tests/` from the live site.

## Verification

Final counts at `eebb0ab`:

| Check | Command | Result |
|---|---|---|
| Static checks | `uv run tests/check_site.py` | 150/150 passed |
| Browser checks, local | `uv run tests/browser_check.py http://127.0.0.1:8000 <dir>` | 182/182 passed |
| Browser checks, live | `uv run tests/browser_check.py https://zidongzhao.github.io <dir>` | 181/181 passed |
| Real phone | Zidong on Android Chrome over home Wi-Fi | 9/9 confirmed |

The live run skips the DOI lookups, which only run locally, and adds checks that the project docs (`SPEC.md`, `SOURCES.md` and others) return 404.

**Static checks** cover the archive and noindex rules, config exclusions, no em dashes, page structure and nav order, font loading and fallbacks, WCAG AA contrast for every text color in both modes, analytics tag, copy rules, email and phone scans, photo size and metadata, publications and DOIs (now inside Academics, after Read more), the resume download, interaction and accessibility rules, redirects, old PDF URLs, sitemap, and broken or archive-bound links.

**Browser checks** run Playwright with Chromium and WebKit. Desktop and narrow-window checks cover horizontal scroll and console errors in both modes, fonts, nav scrolling and highlight, tilt and sweep effects, reduced motion, the phone menu with and without JavaScript, the theme switch, old URLs, DOIs, and served files. Phone profiles (iPhone SE, iPhone 15 and its landscape in WebKit; Pixel 7 and its landscape in Chromium) cover no sideways scroll, a visible Menu, no stuck hover after a tap, the bar staying on screen and slim, labels pinning under the bar, the menu opening mid-page and landing sections below the bar, 44px tap targets, `/#academics` loading below the bar, and Menu staying on screen after rotating with the menu open.

**Real phone checklist** (all confirmed): the bar stays pinned with labels under it; Menu works mid-page; the theme choice survives a reload; no stuck hover; small targets are easy to hit; rotating gives the phone header, also with the menu open; the bar and labels show the texture; smooth scrolling; no sideways scroll.

To test on a phone again: run `uv run python -m http.server 8000 --bind 0.0.0.0` in this folder, open `http://<Mac's Wi-Fi address>:8000` on a phone on the same Wi-Fi, and stop the server afterward. Use only on a trusted home network.

**Not verified:**
- iOS Safari on a real iPhone. Zidong has an Android phone; WebKit in Playwright is close, not exact.
- Safari rendering of the paper texture on a real device.

## Final review (Oct 19)

A fresh reviewer read the whole branch against the spec and probed the running site with Playwright.

**Passed:** no horizontal scroll at 320, 375, and 1280px; readable page with Google Fonts blocked; phone menu usable with JavaScript off; skip link, logical tab order, and visible focus; old HTML URLs landing on the right sections; no email address in served files; nothing private served by Jekyll.

**Important, all fixed in `6777bde` with tests that failed first:**
1. Contact never highlighted in the nav, because the short last section couldn't reach the highlight band.
2. If `site.js` failed to load, phones got a Menu button that did nothing. The script tag now restores the open menu on load failure.
3. Old paper PDF URLs (`/files/*.pdf`) returned 404. The papers now live at those URLs again; the old CV PDF was not republished.

**Deferred minors** (from this review; not fixed or rechecked since):
- Light-mode link hover state is 4.25:1 contrast (forest green on the pink sweep); AA asks for 4.5.
- Sidebar nav and button hover styles have no keyboard-focus counterpart (the focus outline still shows).
- The global focus style changes a button's corner radius from 8px to 4px.
- The no-horizontal-scroll check doesn't test long unbreakable strings added later.
- Two published paper PDFs include an old Princeton office address (standard corresponding-author lines).
- Serif text shifts slightly when Newsreader finishes loading.

## Mobile review (Oct 20)

A code review of the mobile pass found ten issues. Fixed in `6442791`: the resume button was 37px tall; type sizes switched on width alone, so landscape phones got desktop type; fractional viewport widths could match neither layout; rotating with the menu open left a stale bar offset; keyboard focus could scroll a heading under the bar; the bar was first measured too late for a `#section` link.

**Optional, not done:** a guard for browsers without `ResizeObserver`; skipping the bar measurement on desktop; a third fixed-background layer that may cost repaints; a possible texture seam between the bar and pinned labels on iOS.

## Decisions made

| Decision | Why | Cost if wrong |
|---|---|---|
| Worked on branch `revamp` in place, no separate worktree | Fresh clone, nothing else in flight | None |
| Dark-mode muted text lightened from `#7d8c82` to `#87968c` | Failed WCAG AA on cards (4.21:1) | Slightly lighter dates in dark mode |
| Sidebar job title replaced by a focus line | Zidong's request; serves UXR and product DS roles | None |
| Laurie Santos linked in the Yale card, not Academics | Zidong confirmed | None |
| Headshot cropped with a one-off Pillow script outside the project | macOS `sips` ignored crop offsets; Pillow also strips metadata | Re-crop |
| Portfolio card copy kept generic | Portfolio contents unknown | One line of copy |
| `.js` class set in an inline head script as well as in `site.js` | Prevents the phone menu flashing open before the script runs | One inline line |
| Browser checks run with Playwright | Claude in Chrome extension never connected; Zidong chose Playwright | None |
| Resume section made download-only | Zidong's request; Android Chrome and headless browsers can't show inline PDFs anyway | None |
| Papers moved from `assets/papers/` back to `files/` | Scholar and old CVs link to those PDF URLs; GitHub Pages can't redirect PDFs | None |
| Last section given `min-height: 75vh` | Lets Contact reach the active-nav band; a bottom-of-page JS rule wrongly highlighted Contact after clicking Academics | Some empty space below Contact |
| Sticky Menu bar on phones | Zidong's pick; on a long page the menu was otherwise reachable only at the top | About 60px of every phone screen |
| Phone layout also under 500px tall | Landscape phones are wide enough for the sidebar but too short for it | Short desktop windows get the phone header |
| Publications moved into Academics | Zidong's request; papers belong with the academic story, and Projects is for UX work | Old publication links land on Academics |

## Open items

- **Later list (from SPEC.md):** page motion (sliding nav highlight, fade-up sections), the real portfolio URL in place of "Coming soon", personal projects, and moving to Astro only if projects grow into many pages.
- **Untested:** see Verification.

## How to run and update

- Preview: `uv run python -m http.server 8000`, open http://localhost:8000
- Checks: `uv run tests/check_site.py` and `uv run tests/browser_check.py http://127.0.0.1:8000 /tmp/shots` (first time: `uv run --with playwright playwright install chromium webkit`).
- Deploy: merge into `master` and push; GitHub Pages publishes within a few minutes. Then rerun the browser checks against https://zidongzhao.github.io.
