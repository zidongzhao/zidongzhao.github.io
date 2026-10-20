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
        # On phones the label pins just under the sticky Menu bar.
        under = page.evaluate(rect, ".sidebar")["b"] if w < 700 else 0
        check(f"{w}px: current section header pinned at top", abs(top - under) < 2, f"top={top:.0f} bar={under:.0f}")
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

    # Theme switch: follows the system by default, flips on click, remembers the choice
    bg = "() => getComputedStyle(document.body).backgroundColor"
    for scheme, expect in [("light", "false"), ("dark", "true")]:
        ctx = browser.new_context(viewport={"width": 1280, "height": 900}, color_scheme=scheme)
        page = ctx.new_page()
        page.goto(base + "/", wait_until="networkidle")
        if not page.query_selector("#theme-toggle"):
            check(f"{scheme} system: theme switch exists", False)
            ctx.close()
            continue
        check(f"{scheme} system: switch visible and reads {expect}", page.is_visible("#theme-toggle")
              and page.get_attribute("#theme-toggle", "aria-checked") == expect)
        before = page.evaluate(bg)
        page.click("#theme-toggle")
        after = page.evaluate(bg)
        check(f"{scheme} system: click flips the theme", after != before
              and page.get_attribute("#theme-toggle", "aria-checked") != expect, f"{before} -> {after}")
        page.reload(wait_until="networkidle")
        check(f"{scheme} system: choice survives reload", page.evaluate(bg) == after, page.evaluate(bg))
        ctx.close()
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.goto(base + "/", wait_until="networkidle")
    has_switch = page.query_selector("#theme-toggle") is not None
    sw, li = (page.evaluate(rect, "#theme-toggle") if has_switch else {"l": -99, "t": -99, "r": 0, "b": 0}), page.evaluate(rect, ".social a")
    check("desktop: switch sits just below the first icon", sw["t"] >= li["b"] and sw["t"] - li["b"] < 20
          and abs(sw["l"] - li["l"]) < 2, f"switch {sw['l']:.0f},{sw['t']:.0f} icon {li['l']:.0f},{li['b']:.0f}")
    ctx.close()
    ctx = browser.new_context(viewport={"width": 375, "height": 800})
    page = ctx.new_page()
    page.goto(base + "/", wait_until="networkidle")
    has_switch = page.query_selector("#theme-toggle") is not None
    sw, li = (page.evaluate(rect, "#theme-toggle") if has_switch else {"l": -99, "t": -99, "r": 999, "b": -99}), page.evaluate(rect, ".social a")
    check("phone: switch in the icon row, left of the first icon", abs((sw["t"] + sw["b"]) / 2 - (li["t"] + li["b"]) / 2) < 3
          and sw["r"] <= li["l"], f"switch {sw} icon {li}")
    ctx.close()

    # Cards: ink outline with an offset pink shadow, no accent stripe, title above the dates
    for scheme in ["light", "dark"]:
        ctx = browser.new_context(viewport={"width": 1280, "height": 900}, color_scheme=scheme)
        page = ctx.new_page()
        page.goto(base + "/", wait_until="networkidle")
        for sel in ["#experience .card", "#projects .card"]:
            st = page.evaluate("s => { const c = getComputedStyle(document.querySelector(s)); return [c.borderLeftWidth, c.borderTopWidth, c.borderTopLeftRadius, c.boxShadow, c.borderTopColor]; }", sel)
            ink = page.evaluate("() => getComputedStyle(document.querySelector('.name')).color")
            check(f"{scheme} {sel}: even ink border, square corners", st[0] == st[1] and st[2] == "0px" and st[4] == ink, str(st))
            check(f"{scheme} {sel}: offset shadow", "7px 7px 0px" in st[3], st[3])
        photo = page.evaluate("() => { const c = getComputedStyle(document.querySelector('.photo')); return [c.borderTopLeftRadius, c.boxShadow, c.borderTopColor, c.borderTopWidth]; }")
        card = page.evaluate("() => { const c = getComputedStyle(document.querySelector('#experience .card')); return [c.boxShadow, c.borderTopColor, c.borderTopWidth]; }")
        check(f"{scheme}: photo frame matches the card style", photo[0] == "0px" and photo[1:] == card, f"{photo} vs {card}")
        ctx.close()

    # At the top of the page, the ABOUT label's capitals line up with the name's capitals
    cap_top = """s => {
      const el = document.querySelector(s), probe = document.createElement('span');
      probe.style.cssText = 'display:inline-block;width:0;height:0;vertical-align:baseline';
      el.prepend(probe);
      const baseline = probe.getBoundingClientRect().bottom;
      probe.remove();
      const cs = getComputedStyle(el), ctx = document.createElement('canvas').getContext('2d');
      ctx.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
      return baseline - ctx.measureText(el.textContent.trim()[0].toUpperCase()).actualBoundingBoxAscent;
    }"""
    for w in [1280, 900]:
        ctx = browser.new_context(viewport={"width": w, "height": 900})
        page = ctx.new_page()
        page.goto(base + "/", wait_until="networkidle")
        name, about = page.evaluate(cap_top, ".name"), page.evaluate(cap_top, "#about .label")
        check(f"{w}px: ABOUT caps align with the name", abs(name - about) <= 1, f"name {name:.1f} about {about:.1f}")
        ctx.close()

    # Publications dropdown: closed on load, opens on click, keyboard reachable
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.goto(base + "/#projects", wait_until="networkidle")
    has_box = page.query_selector("#projects details summary") is not None
    check("publications hidden on load", has_box and not page.is_visible("#projects .pubs"))
    if has_box:
        page.click("#projects details summary")
        check("publications open on click", page.is_visible("#projects .pubs"))
        seps = page.evaluate("() => [...document.querySelectorAll('#projects .pub')].map(e => getComputedStyle(e).borderTopStyle)")
        check("dotted line between papers", seps[0] == "none" and all(s == "dotted" for s in seps[1:]), str(seps))
        page.focus("#projects details summary"); page.keyboard.press("Enter")
        check("publications close with Enter", not page.is_visible("#projects .pubs"))
    ctx.close()

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
    check("no JS: theme switch hidden", not page.is_visible("#theme-toggle"))
    ctx.close()
    ctx = browser.new_context(viewport={"width": 375, "height": 800})
    page = ctx.new_page()
    page.route("**/js/site.js", lambda r: r.abort())
    page.goto(base + "/")
    page.wait_for_timeout(300)
    check("site.js blocked: nav visible", page.is_visible("#site-nav"))
    ctx.close()

    # Phones: real device profiles, WebKit standing in for iOS Safari, including landscape
    # Tappable area around an element's center, probed with elementFromPoint so invisible hit areas count.
    hit = """e => {
      const r = e.getBoundingClientRect(), cx = r.left + r.width / 2, cy = r.top + r.height / 2;
      const hits = (x, y) => { const t = document.elementFromPoint(x, y); return !!t && (t === e || e.contains(t)); };
      let w = 0, h = 0;
      // Probe just inside the next candidate size, so a 40px box measures 40.
      while (w < 60 && hits(cx - w / 2 - .5, cy) && hits(cx + w / 2 + .5, cy)) w += 2;
      while (h < 60 && hits(cx, cy - h / 2 - .5) && hits(cx, cy + h / 2 + .5)) h += 2;
      return [w, h];
    }"""
    engines = {"chromium": browser, "webkit": p.webkit.launch()}
    for device in ["iPhone SE", "iPhone 15", "iPhone 15 landscape", "Pixel 7", "Pixel 7 landscape"]:
        spec = p.devices[device]
        ctx = engines[spec["default_browser_type"]].new_context(**{k: v for k, v in spec.items() if k != "default_browser_type"})
        page = ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(base + "/", wait_until="networkidle")
        vw = spec["viewport"]["width"]
        sw = page.evaluate("document.documentElement.scrollWidth")
        check(f"{device}: no horizontal scroll", sw <= vw, f"scrollWidth={sw}")
        check(f"{device}: no script errors", not errors, "; ".join(errors[:3]))
        check(f"{device}: phone header with Menu button", page.is_visible("#nav-toggle"))
        check(f"{device}: no hover effects on touch", not page.evaluate("matchMedia('(hover: hover)').matches"))
        icon = page.locator(".social a").first
        icon.hover(); page.wait_for_timeout(400)
        check(f"{device}: icon does not stay tilted after a tap", icon.evaluate("e => getComputedStyle(e).transform") == "none")
        page.screenshot(path=str(out / f"device-{device.replace(' ', '-')}-top.png"))
        if not page.is_visible("#nav-toggle"):
            ctx.close()
            continue

        # Sticky Menu bar: still on screen mid-page, section labels pin below it, menu works from there
        sec = page.evaluate(rect, "#experience")
        page.evaluate(f"window.scrollTo(0, {sec['t']} + window.scrollY + {sec['h']} / 2)")
        page.wait_for_timeout(300)
        bar, tog = page.evaluate(rect, ".sidebar"), page.evaluate(rect, "#nav-toggle")
        check(f"{device}: Menu bar stays on screen", tog["t"] >= 0 and tog["b"] <= 80 and page.is_visible("#nav-toggle"), f"toggle {tog}")
        check(f"{device}: Menu bar is slim", 0 < bar["b"] <= 80, f"bar bottom={bar['b']:.0f}")
        lab = page.evaluate(rect, "#experience .label")
        check(f"{device}: section label pins just below the bar", abs(lab["t"] - bar["b"]) < 2, f"label {lab['t']:.0f} bar {bar['b']:.0f}")
        page.screenshot(path=str(out / f"device-{device.replace(' ', '-')}-scrolled.png"))
        page.tap("#nav-toggle")
        page.wait_for_timeout(200)
        nav = page.evaluate(rect, "#site-nav")
        check(f"{device}: menu opens on screen mid-page", page.is_visible("#site-nav") and nav["t"] >= 0 and nav["b"] <= spec["viewport"]["height"],
              f"nav {nav}")
        page.screenshot(path=str(out / f"device-{device.replace(' ', '-')}-menu.png"))
        sizes = {s: page.locator(s).first.evaluate(hit) for s in ["#nav-toggle", "#theme-toggle", ".social a", "#site-nav a"]}
        page.tap('#site-nav a[href="#academics"]')
        page.wait_for_timeout(1200)
        bar, lab = page.evaluate(rect, ".sidebar"), page.evaluate(rect, "#academics .label")
        check(f"{device}: menu link lands below the bar", not page.is_visible("#site-nav") and lab["t"] >= bar["b"] - 1
              and lab["t"] < bar["b"] + 100, f"label {lab['t']:.0f} bar {bar['b']:.0f}")
        page.locator("#projects .fold > summary").scroll_into_view_if_needed()
        sizes["#projects .fold > summary"] = page.locator("#projects .fold > summary").evaluate(hit)
        page.tap("#projects .fold > summary")
        page.wait_for_timeout(200)
        check(f"{device}: publications open on tap", page.is_visible("#projects .pubs"))
        page.locator(".pub-links a").first.scroll_into_view_if_needed()
        sizes[".pub-links a"] = page.locator(".pub-links a").first.evaluate(hit)
        for s, (w, h) in sizes.items():
            check(f"{device}: {s} tap target at least 44px", w >= 44 and h >= 44, f"{w}x{h}")
        ctx.close()
    engines["webkit"].close()

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
