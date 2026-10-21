# zidongzhao.github.io revamp

## Problem and user

Zidong is a senior quantitative UX researcher looking for their next role. The current site (zidongzhao.github.io) still presents them as a Yale research scientist with a fully academic framing, an empty CV page, and leftover placeholders. Visitors are hiring managers and recruiters, as well as peers in the research, insights, and product fields, usually arriving from LinkedIn, a resume, or a name search.

After ten seconds they should know: a senior quant UXR. Positioning line (Zidong's wording, use verbatim): "I study how people interact with complex technology, and turn what I learn into metrics and product decisions." Proof points, named concretely: Instagram Reels ranking, an LLM-based content classifier, AI-native research workflows adopted by a team of 12, 1.5M+ users at Yale, PhD-level modeling and experimentation. Recommendation systems appear as past work and evidence, never as the brand.

## Goals, non-goals, anti-goals

- **Goal:** one simple, credible page that complements LinkedIn: a narrative of the career path, the work, a portfolio link, the resume, and the academic background.
- **Non-goals:** blog, CMS, contact form, analytics dashboards, per-project pages, password protection on this site.
- **Anti-goals:** reading as an academic site; copying LinkedIn bullet for bullet; showing anything confidential from Instagram beyond what the resume already states; publishing the phone number or a scrapeable email; animations that feel gimmicky or block reading.

## Core flow

Visitor lands, reads the About, scans Experience, then either opens the portfolio, reads or downloads the resume, or try to get in touch via the multiple contact channels.

## Page structure (single scrolling page, in this order)

1. **About.** Opens with the positioning line, then three short paragraphs: Instagram (how people's experience of Reels connects to its ranking and recommendation backend, sentiment measurement, content safety and personalization), Yale and the Princeton PhD, then the toolkit (quantitative methods first, qualitative methods as the complement). About gives the arc; numbers and specifics live in the Experience cards.
2. **Experience.** Cards, newest first: Instagram (Senior Quant UXR, Reels Relevance, Aug 2025 to Sep 2026), HelloNova (Advisor, Aug 2024 to Feb 2026), Yale Science of Well-Being (Research Scientist, Aug 2021 to Aug 2025), Princeton (PhD researcher and graduate instructor, Sep 2016 to May 2021). Two or three lines each, drawn from resume and LinkedIn, phrased to complement rather than repeat LinkedIn. Numbers spelled one way ("more than 10", "about 100"). No Meta-internal figures beyond what LinkedIn states publicly (no funding amount, no impression share). HelloNova is described as an early-stage startup that went through several pivots; the link goes to what it became (NovaLand) without implying the research was on that product. The Princeton card lists the methods; Academics covers the questions, people, and dissertation.
3. **Projects.** UX research portfolio card: the portfolio is hosted elsewhere; the button reads "Coming soon" and is not a live link until Zidong supplies the URL.
4. **Resume.** A "Download resume (PDF)" button only. Zidong dropped the summary line and the inline viewer (October 2026).
5. **Academics.** One short paragraph each on the Princeton and Vanderbilt work. Below them, a collapsed dropdown titled "Read more about my academic work" (same +/× style as the publications dropdown) holds the three research themes from the old `research.html`, in past tense, with collaborators linked inline. Right after it, a second collapsed dropdown, "Academic publications" (moved here from Projects, October 2026; dotted lines between papers): the 5 papers from the current site, each with PDF and DOI links (DOIs and PDFs below). The old publication URLs redirect to Academics. Mentors named on the old homepage (Diana Tamir, Tom Griffiths, Laurie Santos, Bunmi Olatunji, Sohee Park) keep their links. No posters. Start the section with something like "In a previous life, I did experimental, computational, and neuroimaging work in psychology in academia" 
6. **Contact.** Email shown as plain text "zhaozidong1993 at gmail dot com", with no `mailto:` link and no address in the HTML source in usable form. Social icons: LinkedIn, GitHub, Google Scholar.

**Sidebar (desktop):** pinned left. Name in serif ("Zidong Zhao"), 赵紫东, then the focus line "UX Research · Product Data Science · Behavioral Insights" in green semibold, standing in for a job title (no "Quantitative UX Researcher" line; toolkit details live in About), section links, social icons. **Widths:** at 1100px and up the sidebar (300px) and reading column (70ch) keep their widths, and extra width becomes whitespace split 1 : 2 : 6 (left margin, gap, right margin). From 700 to 1099px a narrower 240px sidebar stays beside the content. Under 700px wide, or under 500px tall (phones turned sideways), the sidebar becomes a compact top header: 赵紫东 beside the name, then the focus line, then Menu and icons on one row, with the menu opening below. On scroll the name and focus line scroll away and the Menu row stays pinned as a slim bar; section labels pin just below it (Zidong's pick, October 2026). Every control is at least 44px to tap, and hover effects apply only to mouse and trackpad. No horizontal scroll at any width.

## Visual system (decided in mockups)

Light mode:
- Page background: light sage `#eef6f0`
- Highlights (title, section labels, links): forest green `#3d7a48`
- Background texture: sparse recycled-paper flecks (tiny ink specks plus medium pink flecks), inline SVG noise in two layers. Light mode uses forest-green specks and deeper pink flecks (`#2f6b3b`, `#d0679a`) so they show at normal screen density; dark mode runs at 50% strength. Pinned section labels carry the same texture.
- Cards (experience and portfolio) and the headshot frame: square corners, 1.5px ink border, solid 7px offset shadow in a soft pink (`--card-shadow`: `#f7cfe1` light, `#8a5a70` dark), no accent stripe. Title first, then dates and place, then the description.
- Decorations (sidebar divider, card edges, active nav item, link hover sweep): pink, `#f9d9e8` divider, `#f6d3e3` card border, `#f2b8d2` card left edge, `#fbe3ef` soft fill
- Cards: `#fffafd`; ink `#1f2a22`; muted `#5a675e`
- Fonts: see Type below

Dark mode follows the visitor's system setting by default. A sun/moon switch sits just below the LinkedIn icon in the sidebar (on phones, in the icon row left of LinkedIn); a choice made there is remembered in the browser and applied before first paint. Without JavaScript the switch is hidden and the system setting still applies. Dark tokens:
- Background deep pine `#16201a`; cards `#1e2a23` with `#33463a` border
- Highlights soft mint `#8fd19e`; decorations dusty rose `#d98fb0`, soft fill `#4a2e3c`, divider `#5a3a4a`
- Ink `#eef6f0`; body `#c9d6cc`; muted `#7d8c82`

Contrast for body text and links must meet WCAG AA in both modes; adjust shades (not hues) if a pair fails.

### Type (decided in mockups)

Fonts, all from Google Fonts with `display=swap`:
- **Serif: Newsreader**, weight 500, plus 400 italic. Used only for the name and the About positioning line (italic 400 also for journal names in Publications).
- **Sans: IBM Plex Sans**, weights 400, 500, 600. Everything else: sidebar text, section labels, body, cards, buttons.
- **Chinese name: Long Cang** (casual handwriting, fallback Kaiti), weight 400, loaded with `&text=赵紫东` so only those three glyphs download.
- Fallbacks: `Newsreader, Georgia, serif` and `"IBM Plex Sans", system-ui, -apple-system, sans-serif`. Apply `font-size-adjust` on the sans stack so a fallback font keeps the same lowercase height and the layout doesn't shift while fonts load.

Scale (rem at a 16px root; desktop / phone):

| Role | Font | Size | Weight | Line height |
|---|---|---|---|---|
| Name (sidebar or phone header) | Newsreader | 2.5 (2 under 1100px) / 2 | 500 | 1.05 |
| 赵紫东 | Long Cang | 1.75 / 1.4 | 400 | 1.3 |
| Positioning line (About opener) | Newsreader | 1.5 / 1.25 | 500 | 1.35 |
| Focus line in sidebar | Plex, green | 0.95 | 600 | 1.4 |
| Nav links | Plex | 0.95 | 500 | 1.5 |
| Section label (ABOUT, EXPERIENCE...) | Plex, uppercase, 0.12em tracking | 1.0625 | 600 | 1.2 |
| Body text | Plex | 1.0625 / 1.0 | 400 | 1.65 |
| Card title (role and org) | Plex | 1.0625 | 600 | 1.4 |
| Meta (dates, places) | Plex | 0.875 | 400 | 1.4 |
| Buttons | Plex | 0.9375 | 500 | 1 |

Body text lines stay under about 70 characters. Name and positioning line are the only serif text; that restraint is the point.

## Interactions (decided)

- Text links: pink highlight sweeps across on hover.
- Social icons: playful tilt and grow on hover.
- Links to other sites and the paper PDFs open in a new tab (`rel="noopener"`); the resume button downloads.
- Section labels stay pinned at the top of the window while their section is on screen; the next label pushes the previous one off.
- Experience and portfolio cards: tilt toward the cursor (the edge nearest it lifts forward), at most 2° per axis.
- All of the above also respond to keyboard focus where it makes sense, and are off under `prefers-reduced-motion`. Card tilt is off on touch devices.

## Stack and deploy (decided)

- Plain HTML, CSS, and a small vanilla JS file. No framework, no build step, no package manager.
- Hosted on GitHub Pages from the existing repo `github.com/zidongzhao/zidongzhao.github.io`, so the URL and git history are kept.
- The entire current site (every file and folder, structure unchanged) is moved into `old-site/` in that repo as a reference copy. It stays publicly reachable; mark its pages `noindex` and disallow it in `robots.txt`. Its root-relative links will not work from the subfolder; that is accepted. Old PDFs that contain contact details (`files/CV_Zidong Zhao_041621.pdf`, `Resume_Zidong Zhao_ds1p.pdf`, and the copy under `backup_20250322_112858/`) stay in the archive unchanged; Zidong accepted this on the condition that the folder is not indexed. No page on the new site links into `old-site/`.
- Keep at the repo root: the Google Analytics tag (`G-L9Q1GGPFNJ`), `google60a4458eb7076ec4.html` (Search Console verification), favicons. Update `sitemap.xml` to the new single page.
- Publication PDFs move to the new site's own folder (copied out of the archive) so the new page doesn't depend on `old-site/`.

## Who sees what

Everything in the repo is public. Nothing confidential goes in. No phone number anywhere, including in the resume PDF. The portfolio lives off-site under Zidong's own access control.

## Sources

- Resume and LinkedIn text, copied into `SOURCES.md` (phone number omitted).
- Current site repo for academic text, publications, collaborator links, PDFs.
- Links: LinkedIn `https://www.linkedin.com/in/zidong-zhao-10076559/`, GitHub `https://github.com/zidongzhao/`, Scholar `https://scholar.google.com/citations?user=AtnndQsAAAAJ`.
- DOIs: 10.1016/j.jesp.2023.104521, 10.1037/emo0000890, 10.1017/S0140525X19003133, 10.1037/xge0000565, 10.1080/02699931.2015.1110117.

## Inputs Zidong provides

- Resume PDF exported from the Google Doc with the phone number removed.
- Final approval of all copy before deploy. New copy uses only facts from the sources above.

## Calls made without explicit sign-off (check these)

- Instagram is written in the past tense (resume says the role ended Sep 2026; LinkedIn still says Present).
- HelloNova is included although it's not on the resume.
- Princeton appears in both Experience and Academics: the card lists methods and teaching, Academics tells the research story.
- The resume PDF keeps the email address, because recruiters expect it there. The no-scrapeable-email rule applies to the HTML only.
- Old top-level URLs (`/cv.html`, `/publications.html`, `/research.html`, `/contact.html`, `/collaborators.html`, `/publications/*.html`) get tiny redirect pages to the matching section of the new page, so inbound links from Scholar and old CVs keep working.
- `SOURCES.md` is gitignored, since the repo is public and it holds the plain email address.
- The BBS paper links to the full commentary issue PDF at `#page=52`, as the old site did.

## Left to the builder

Exact copy wording (for Zidong's review), spacing, icon source (inline SVG preferred over the old PNGs), scroll-highlighting of the active nav item, file layout inside the repo.

## End-to-end check

Served locally (`python -m http.server` via uv, or any static server): at desktop width and at 375px width, in light and dark mode, all six sections render; the sidebar links scroll to the right sections; the resume download returns the file; all publication PDF and DOI links resolve; the hover effects work and stop under reduced motion; no email address appears in the HTML source and no phone number appears in the HTML or the new resume PDF; the old URLs redirect; `old-site/index.html` exists with its original structure. After deploy, the same checks pass on zidongzhao.github.io.

## Later

- Page motion: sliding highlight in the sidebar and sections that fade up on scroll. Decide per section once the real page exists.
- Portfolio URL to replace "Coming soon".
- Personal projects as entries in Projects once they exist; move to Astro if they grow into many pages.
