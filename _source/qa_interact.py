#!/usr/bin/env python3
"""Interaction QA: drawer, language switching + persistence, form behaviour."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(".")
SHOTS = "/tmp/shots"
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


with sync_playwright() as p:
    b = p.chromium.launch()

    # ---------- Mobile drawer, in Arabic (RTL) and English -----------------
    for lang in ["en", "ar"]:
        ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        pg = ctx.new_page()
        pg.goto(f"file://{ROOT}/index.html?lang={lang}")
        pg.wait_for_timeout(400)
        pg.click("#navToggle")
        pg.wait_for_timeout(600)
        check(pg.evaluate("()=>document.body.classList.contains('nav-open')"), f"{lang}: drawer did not open")
        box = pg.evaluate("()=>{const r=document.getElementById('mobileNav').getBoundingClientRect();"
                          "return {l:r.left,r:r.right};}")
        check(box["l"] > -1 and box["r"] < 391, f"{lang}: drawer off-screen when open {box}")
        pg.screenshot(path=f"{SHOTS}/drawer-{lang}.png")
        # Escape closes it
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(500)
        check(not pg.evaluate("()=>document.body.classList.contains('nav-open')"), f"{lang}: Escape did not close drawer")
        ctx.close()

    # ---------- Language switcher (segmented pill) + persistence -----------
    ctx = b.new_context(viewport={"width": 1440, "height": 960})
    pg = ctx.new_page()
    pg.goto(f"file://{ROOT}/index.html")
    pg.wait_for_timeout(400)
    check(pg.is_visible(".lang .lang-btn[data-lang='ar']"), "language switcher buttons not visible")
    px_en = pg.evaluate("()=>getComputedStyle(document.querySelector('.lang-pill')).getPropertyValue('--px')")

    pg.click(".lang .lang-btn[data-lang='de']")
    pg.wait_for_timeout(1300)   # swap sequence: 250ms out + ~700ms arrive
    px_de = pg.evaluate("()=>getComputedStyle(document.querySelector('.lang-pill')).getPropertyValue('--px')")
    check(px_en != px_de, f"language pill did not slide ({px_en} -> {px_de})")
    check(pg.evaluate("()=>!document.documentElement.classList.contains('lang-swapping') && "
                      "!document.documentElement.classList.contains('lang-arriving')"),
          "language-swap classes left on <html>")
    pg.screenshot(path=f"{SHOTS}/langswitch-de.png", clip={"x": 900, "y": 0, "width": 540, "height": 120})
    check(pg.evaluate("()=>document.documentElement.lang") == "de", "switching to German failed")

    # Navigate with a plain link — the choice must survive
    pg.click("a.nav-link[href='services.html']")
    pg.wait_for_load_state("load")
    pg.wait_for_timeout(500)
    check(pg.evaluate("()=>document.documentElement.lang") == "de", "German did not persist across pages")
    check("Leistungen" in pg.title(), f"German title not applied: {pg.title()!r}")

    # German -> Arabic is the exact path that used to leave German on screen
    pg.click(".lang .lang-btn[data-lang='ar']")
    pg.wait_for_timeout(1300)
    check(pg.evaluate("()=>document.documentElement.dir") == "rtl", "Arabic did not set RTL")
    body = pg.evaluate("()=>document.body.innerText")
    for w in ["Buchhaltung", "Leistungen", "Unternehmen", "Steuerberatung", "Kontakt"]:
        check(w not in body, f"GERMAN LEAKED INTO ARABIC: {w!r}")

    # Reload should come back in Arabic
    pg.goto(f"file://{ROOT}/pricing.html")
    pg.wait_for_timeout(500)
    check(pg.evaluate("()=>document.documentElement.lang") == "ar", "Arabic did not persist after reload")
    ctx.close()

    # ---------- Contact form -----------------------------------------------
    ctx = b.new_context(viewport={"width": 1440, "height": 960})
    pg = ctx.new_page()
    pg.goto(f"file://{ROOT}/contact.html?lang=de")
    pg.wait_for_timeout(400)

    pg.click("#sendWhatsApp")      # empty -> should flag three fields
    pg.wait_for_timeout(250)
    errs = pg.evaluate("()=>Array.from(document.querySelectorAll('.field.has-error .field-error'))"
                       ".map(e=>e.textContent.trim())")
    check(len(errs) == 3, f"expected 3 validation errors, got {errs}")
    check(all("Bitte" in e for e in errs), f"validation errors not in German: {errs}")
    pg.screenshot(path=f"{SHOTS}/form-errors-de.png", clip={"x": 700, "y": 250, "width": 700, "height": 700})

    pg.fill("#f-name", "Max Mustermann")
    pg.fill("#f-email", "max@example.com")
    pg.fill("#f-message", "Ich hätte gerne ein Erstgespräch zur Buchhaltung.")
    pg.select_option("#f-topic", "vat")

    # Intercept the WhatsApp hand-off instead of actually opening it
    pg.evaluate("()=>{window.__opened=null; window.open=(u)=>{window.__opened=u;};}")
    pg.click("#sendWhatsApp")
    pg.wait_for_timeout(350)
    url = pg.evaluate("()=>window.__opened")
    check(url and "wa.me/971508821960" in url, f"WhatsApp hand-off wrong: {url}")
    check(url and "Mustermann" in url.replace("%20", " ").replace("+", " ") or
          (url and "Mustermann" in __import__("urllib.parse", fromlist=["unquote"]).unquote(url)),
          "form contents missing from WhatsApp message")
    check(pg.is_visible("#formStatus.is-visible"), "no confirmation shown after sending")
    ctx.close()

    # ---------- Scroll behaviour: reveals fire on scroll, ring appears ------
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    pg.goto(f"file://{ROOT}/index.html")
    pg.wait_for_timeout(3600)   # past the old "reveal everything at 2.5s" fail-safe
    pg.evaluate("()=>{document.documentElement.style.scrollBehavior='auto'}")
    below = pg.evaluate("()=>document.querySelectorAll('.reveal:not(.is-visible)').length")
    check(below > 0, "all .reveal elements were revealed without scrolling (fail-safe firing too early)")
    check(not pg.evaluate("()=>document.getElementById('toTop').classList.contains('is-on')"),
          "back-to-top ring visible at the top of the page")
    pg.evaluate("()=>scrollTo(0, 1400)")
    pg.wait_for_timeout(900)
    check(pg.evaluate("()=>document.getElementById('toTop').classList.contains('is-on')"),
          "back-to-top ring did not appear after scrolling")
    pg.click("#toTop")
    pg.wait_for_timeout(1400)
    check(pg.evaluate("()=>scrollY") < 5, "back-to-top did not return to the top")
    ctx.close()

    # ---------- Reduced motion: content must not stay invisible -------------
    ctx = b.new_context(viewport={"width": 1440, "height": 960}, reduced_motion="reduce")
    pg = ctx.new_page()
    pg.goto(f"file://{ROOT}/index.html")
    pg.wait_for_timeout(600)
    hidden = pg.evaluate("()=>Array.from(document.querySelectorAll('.reveal'))"
                         ".filter(e=>getComputedStyle(e).opacity==='0').length")
    check(hidden == 0, f"{hidden} elements invisible under prefers-reduced-motion")
    ctx.close()

    b.close()

print("=" * 60)
print("\n".join("  • " + f for f in fails) if fails else "ALL INTERACTION CHECKS PASSED")
print("=" * 60)
