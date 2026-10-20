# /// script
# dependencies = ["playwright"]
# ///
"""Browser checks for SPEC.md's end-to-end list. Usage: browser_check.py BASE_URL OUT_DIR"""
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

base, out = sys.argv[1].rstrip("/"), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


with sync_playwright() as p:
    browser = p.chromium.launch()
    for scheme in ["light", "dark"]:
        for w, h in [(1280, 900), (800, 1000), (375, 800), (320, 700)]:
            ctx = browser.new_context(viewport={"width": w, "height": h}, color_scheme=scheme)
            page = ctx.new_page()
            errors = []
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(base + "/", wait_until="networkidle")
            sw = page.evaluate("document.documentElement.scrollWidth")
            check(f"{scheme} {w}px no horizontal scroll", sw <= w, f"scrollWidth={sw}")
            check(f"{scheme} {w}px no console errors", not errors, "; ".join(errors[:3]))
            page.screenshot(path=str(out / f"{scheme}-{w}-top.png"))
            page.screenshot(path=str(out / f"{scheme}-{w}-full.png"), full_page=True)
            ctx.close()

    # Layout across widths: SPEC.md "Layout"
    rect = "s => { const r = document.querySelector(s).getBoundingClientRect(); return {l: r.left, r: r.right, t: r.top, b: r.bottom, w: r.width, h: r.height}; }"
    ctx = browser.new_context(viewport={"width": 2560, "height": 1300})
    page = ctx.new_page()
    page.goto(base + "/", wait_until="networkidle")
    sb, mn = page.evaluate(rect, ".sidebar"), page.evaluate(rect, "main")
    left, gap, right = sb["l"], mn["l"] - sb["r"], 2560 - mn["r"]
    check("2560px: whitespace left:gap:right is 1:2:6", left > 50 and abs(gap - 2 * left) < 3 and abs(right - 6 * left) < 6,
          f"{left:.0f}/{gap:.0f}/{right:.0f}")
    sec = page.evaluate(rect, "#about")
    check("2560px: reading column keeps its width", abs(mn["w"] - sec["w"]) < 2 and 600 < sec["w"] < 760, f"main={mn['w']:.0f} section={sec['w']:.0f}")
    page.screenshot(path=str(out / "layout-2560.png"))
    ctx.close()
    ctx = browser.new_context(viewport={"width": 800, "height": 1000})
    page = ctx.new_page()
    page.goto(base + "/", wait_until="networkidle")
    sb, mn = page.evaluate(rect, ".sidebar"), page.evaluate(rect, "main")
    check("800px: sidebar beside content", sb["r"] <= mn["l"] + 1 and mn["t"] < 50, f"sidebar r={sb['r']:.0f} main l={mn['l']:.0f} t={mn['t']:.0f}")
    ctx.close()
    ctx = browser.new_context(viewport={"width": 375, "height": 800})
    page = ctx.new_page()
    page.goto(base + "/", wait_until="networkidle")
    hd, nm, zh = page.evaluate(rect, ".sidebar"), page.evaluate(rect, ".name"), page.evaluate(rect, ".name-zh")
    # About 40% shorter than the stacked header it replaced (318px).
    check("375px: header at most 195px tall", hd["h"] <= 195, f"h={hd['h']:.0f}")
    check("375px: 赵紫东 beside the name", zh["l"] > nm["r"] and zh["t"] < nm["b"], f"name r={nm['r']:.0f} zh l={zh['l']:.0f}")
    ctx.close()

    # Section headers: larger label that stays pinned while its section is on screen
    for w, h in [(1280, 900), (375, 800)]:
        ctx = browser.new_context(viewport={"width": w, "height": h})
        page = ctx.new_page()
        page.goto(base + "/", wait_until="networkidle")
        label = page.locator("#experience .label")
        check(f"{w}px: section label is 17px", label.evaluate("e => getComputedStyle(e).fontSize") == "17px",
              label.evaluate("e => getComputedStyle(e).fontSize"))
        sec = page.evaluate(rect, "#experience")
        page.evaluate(f"window.scrollTo(0, {sec['t']} + window.scrollY + {sec['h']} / 2)")
        page.wait_for_timeout(200)
        top = page.evaluate(rect, "#experience .label")["t"]
        check(f"{w}px: current section header pinned at top", abs(top) < 2, f"top={top:.0f}")
        ctx.close()

    # Paper texture: on the page in both modes, and repeated on pinned labels so they don't read as flat bands
    paper = {}
    for scheme in ["light", "dark"]:
        ctx = browser.new_context(viewport={"width": 1280, "height": 900}, color_scheme=scheme)
        page = ctx.new_page()
        page.goto(base + "/", wait_until="networkidle")
        style = "s => { const c = getComputedStyle(document.querySelector(s)); return [c.backgroundImage, c.backgroundAttachment]; }"
        body, lab = page.evaluate(style, "body"), page.evaluate(style, "#experience .label")
        paper[scheme] = body[0]
        check(f"{scheme}: paper texture on page", "svg" in body[0] and body[1].startswith("fixed"), body[1])
        check(f"{scheme}: pinned label carries the same texture", lab == body, lab[1])
        ctx.close()
    check("dark mode has its own, softer texture", paper["light"] != paper["dark"])

    # Desktop interactions
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.goto(base + "/", wait_until="networkidle")
    check("fonts loaded", page.evaluate("document.fonts.check('500 20px Newsreader') && document.fonts.check('16px \"IBM Plex Sans\"')"))
    page.click('#site-nav a[href="#academics"]')
    page.wait_for_timeout(1200)
    top = page.evaluate("document.getElementById('academics').getBoundingClientRect().top")
    check("nav click scrolls to section", -5 < top < 120, f"top={top}")
    check("active nav follows scroll", page.get_attribute('#site-nav a[href="#academics"]', "aria-current") == "true")
    # Contact is short and never reaches the observer band, so it needs its own case.
    page.click('#site-nav a[href="#contact"]')
    page.wait_for_timeout(1200)
    check("active nav marks Contact at page end", page.get_attribute('#site-nav a[href="#contact"]', "aria-current") == "true")
    page.goto(base + "/#experience", wait_until="networkidle")
    card = page.locator("#experience .card").first
    card.scroll_into_view_if_needed()
    b = card.bounding_box()
    page.mouse.move(b["x"] + b["width"] * 0.9, b["y"] + b["height"] * 0.2)
    page.wait_for_timeout(300)
    tf = card.evaluate("e => e.style.transform") or ""
    rot = {k: float(v) for k, v in re.findall(r"rotate([XY])\((-?[\d.]+)deg\)", tf)}
    # Cursor is right of and above center. In CSS, negative rotateY brings the right edge forward
    # and negative rotateX brings the top edge forward.
    check("card tilts toward cursor", rot.get("Y", 0) < 0 and rot.get("X", 0) < 0, tf)
    check("card tilt is gentle", rot and max(abs(v) for v in rot.values()) <= 2.5, tf)
    page.screenshot(path=str(out / "hover-card.png"))
    pcard = page.locator("#projects .card").first
    pcard.scroll_into_view_if_needed()
    b = pcard.bounding_box()
    page.mouse.move(b["x"] + b["width"] * 0.9, b["y"] + b["height"] * 0.2)
    page.wait_for_timeout(300)
    check("portfolio card tilts too", "rotateY(-" in (pcard.evaluate("e => e.style.transform") or ""))
    icon = page.locator(".social a").first
    icon.hover(); page.wait_for_timeout(400)
    check("social icon tilts on hover", icon.evaluate("e => getComputedStyle(e).transform") != "none")
    link = page.locator("#academics .prose a, #academics a").first
    link.hover(); page.wait_for_timeout(500)
    check("link sweep fills on hover", "100%" in link.evaluate("e => getComputedStyle(e).backgroundSize"))
    page.screenshot(path=str(out / "hover-link.png"))
    resp = page.request.get(base + "/assets/Zidong-Zhao-Resume.pdf")
    check("resume PDF served", resp.ok and resp.headers.get("content-type", "").startswith("application/pdf"))
    page.locator("#resume").scroll_into_view_if_needed()
    page.screenshot(path=str(out / "resume.png"))
    ctx.close()

    # Reduced motion: no tilt, no transform on hover
    ctx = browser.new_context(viewport={"width": 1280, "height": 900}, reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(base + "/#experience", wait_until="networkidle")
    card = page.locator("#experience .card").first
    b = card.bounding_box()
    page.mouse.move(b["x"] + b["width"] * 0.9, b["y"] + b["height"] * 0.2)
    page.wait_for_timeout(300)
    check("reduced motion: no card tilt", not card.evaluate("e => e.style.transform"))
    icon = page.locator(".social a").first
    icon.hover(); page.wait_for_timeout(300)
    check("reduced motion: icon does not move", icon.evaluate("e => getComputedStyle(e).transform") == "none")
    ctx.close()

    # Phone menu with and without JS
    ctx = browser.new_context(viewport={"width": 375, "height": 800}, has_touch=True)
    page = ctx.new_page()
    page.goto(base + "/", wait_until="networkidle")
    check("phone: menu collapsed with JS", not page.is_visible("#site-nav"))
    page.click("#nav-toggle")
    check("phone: toggle opens menu", page.is_visible("#site-nav") and page.get_attribute("#nav-toggle", "aria-expanded") == "true")
    page.screenshot(path=str(out / "phone-menu-open.png"))
    page.click('#site-nav a[href="#contact"]')
    page.wait_for_timeout(300)
    check("phone: menu closes after link", not page.is_visible("#site-nav"))
    ctx.close()
    ctx = browser.new_context(viewport={"width": 375, "height": 800}, java_script_enabled=False)
    page = ctx.new_page()
    page.goto(base + "/")
    check("no JS: nav visible", page.is_visible("#site-nav"))
    check("no JS: toggle hidden", not page.is_visible("#nav-toggle"))
    ctx.close()
    ctx = browser.new_context(viewport={"width": 375, "height": 800})
    page = ctx.new_page()
    page.route("**/js/site.js", lambda r: r.abort())
    page.goto(base + "/")
    page.wait_for_timeout(300)
    check("site.js blocked: nav visible", page.is_visible("#site-nav"))
    ctx.close()

    # Old URLs and DOIs
    ctx = browser.new_context()
    page = ctx.new_page()
    for old, sid in [("/cv.html", "resume"), ("/publications/ZhaoSenedTamir2023.html", "projects"), ("/research.html", "academics")]:
        page.goto(base + old)
        page.wait_for_url(f"**/#{sid}", timeout=5000)
        check(f"{old} lands on #{sid}", page.url.endswith(f"/#{sid}"), page.url)
    if "localhost" in base or "127.0.0.1" in base:
        for doi in ["10.1016/j.jesp.2023.104521", "10.1037/emo0000890", "10.1017/S0140525X19003133",
                    "10.1037/xge0000565", "10.1080/02699931.2015.1110117"]:
            r = page.request.get(f"https://doi.org/api/handles/{doi}")
            check(f"DOI {doi} resolves", r.ok and '"responseCode":1' in r.text().replace(" ", ""))
    for pdf in ["ZhaoSenedTamir2023", "ZhaoThorntonTamir2020", "BBS2020_PredictiveSubstrate", "MeyerZhaoTamir2019", "OlatunjiBergZhao2017"]:
        r = page.request.get(f"{base}/files/{pdf}.pdf")
        check(f"paper {pdf} served", r.ok)
    for hidden in ["/SPEC.md", "/SOURCES.md", "/CLAUDE.md", "/tests/check_site.py"]:
        if "github.io" in base:
            check(f"{hidden} not served", page.request.get(base + hidden).status == 404)
    ctx.close()
    browser.close()

failed = [r for r in results if not r[1]]
for name, ok, detail in results:
    print(f"{'PASS' if ok else 'FAIL'}  {name}{'  (' + detail + ')' if detail and not ok else ''}")
print(f"\n{len(results) - len(failed)}/{len(results)} passed; screenshots in {out}")
sys.exit(1 if failed else 0)
