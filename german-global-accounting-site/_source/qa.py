#!/usr/bin/env python3
"""
Visual + automated QA across every page x language x breakpoint.

Checks performed on each combination:
  * horizontal overflow (element wider than the viewport)
  * untranslated keys left on screen (raw key names leaking through)
  * foreign-script / foreign-word leakage between languages
  * console errors, including the i18n engine's own missing-key warnings
  * document direction and lang attributes
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
import re, sys, json
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(".")
PAGES = ["index.html", "about.html", "services.html", "pricing.html", "contact.html"]
LANGS = ["en", "de", "ar"]
VIEWPORTS = {"desktop": (1440, 960), "mobile": (390, 844)}
SHOT_DIR = "/tmp/shots"

# Words that must never appear in another language's rendering.
GERMAN_MARKERS = ["Buchhaltung", "Leistungen", "Unternehmen", "Über uns", "Preise",
                  "Kontakt", "vereinbaren", "Zuverlässig", "Nachricht", "Sprache",
                  "Startseite", "Beratung", "Unterstützung", "Steuerberatung"]
ENGLISH_MARKERS = ["Bookkeeping", "Services", "Pricing", "Contact", "About",
                   "Consultation", "Reliable", "Message", "Language", "Home",
                   "Business", "Support", "Accounting"]
ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
LATIN_WORD_RE = re.compile(r"[A-Za-zÀ-ÿ]{3,}")

# Proper nouns and technical terms that legitimately stay Latin everywhere.
ALLOWED_LATIN = {
    "german", "global", "accounting", "llc", "whatsapp", "vat", "ifrs", "com",
    "gmail", "germanglobalacc", "name", "company", "english", "deutsch",
}

os.makedirs(SHOT_DIR, exist_ok=True)
problems = []

CONTRAST_JS = r"""()=>{
  const lum = c => {
    const p = c.match(/[\d.]+/g);
    if (!p) return 1;
    const [r,g,b] = p.slice(0,3).map(Number).map(v => {
      v /= 255;
      return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4);
    });
    return 0.2126*r + 0.7152*g + 0.0722*b;
  };
  // Walk up for the first effectively-opaque background
  const bgOf = el => {
    let n = el;
    while (n && n !== document.documentElement) {
      const c = getComputedStyle(n).backgroundColor;
      const a = c.match(/[\d.]+/g);
      if (a && (a.length < 4 || Number(a[3]) > 0.85)) return c;
      n = n.parentElement;
    }
    return 'rgb(247,247,244)';
  };
  const out = [];
  document.querySelectorAll('h1,h2,h3,h4,p,li,a,button,dd,dt,label,address,figcaption')
    .forEach(el => {
      if (!el.textContent.trim()) return;
      if (el.closest('.lang')) return;   // white text on the sliding pill (a sibling layer)
      // only leaf-ish text holders, so we don't measure wrappers
      if (el.querySelector('h1,h2,h3,h4,p,li,a,button,dd,dt,label')) return;
      const cs = getComputedStyle(el);
      if (cs.visibility === 'hidden' || cs.display === 'none') return;
      if (parseFloat(cs.opacity) < 0.1) return;
      const r = el.getBoundingClientRect();
      if (!r.width || !r.height) return;
      if (r.bottom < 0 || r.right < 0) return;      // off-canvas drawer
      const fg = lum(cs.color), bg = lum(bgOf(el));
      const ratio = (Math.max(fg,bg) + 0.05) / (Math.min(fg,bg) + 0.05);
      const size = parseFloat(cs.fontSize);
      const weight = parseInt(cs.fontWeight) || 400;
      const large = size >= 24 || (size >= 18.66 && weight >= 700);
      if (ratio < (large ? 3 : 4.5)) {
        out.push(el.tagName.toLowerCase() + '.' + String(el.className || '').split(' ')[0]
                 + ' ratio=' + ratio.toFixed(2)
                 + ' "' + el.textContent.trim().slice(0, 30) + '"');
      }
    });
  return out.slice(0, 10);
}"""


# Strings that legitimately appear in every language: the registered company
# name, and the language picker's native labels (showing each language in its
# own script is the universal convention, not a language mix).
ALWAYS_ALLOWED = ["German Global Accounting LLC", "German Global Accounting",
                  "العربية", "Deutsch", "English", "WhatsApp", "ع"]


def check_leak(lang, text):
    """Return a list of suspected cross-language leaks in the rendered text."""
    for a in ALWAYS_ALLOWED:
        text = text.replace(a, " ")
    found = []
    if lang == "ar":
        # Any Latin word that is not an allowed proper noun is suspicious
        for w in set(LATIN_WORD_RE.findall(text)):
            if w.lower() not in ALLOWED_LATIN:
                found.append("latin-in-arabic:" + w)
    else:
        if ARABIC_RE.search(text):
            found.append("arabic-in-" + lang)
        markers = GERMAN_MARKERS if lang == "en" else ENGLISH_MARKERS
        for m in markers:
            if re.search(r"\b" + re.escape(m) + r"\b", text):
                found.append(("german-in-en:" if lang == "en" else "english-in-de:") + m)
    return found


with sync_playwright() as p:
    browser = p.chromium.launch()
    for vp_name, (w, h) in VIEWPORTS.items():
        for lang in LANGS:
            ctx = browser.new_context(viewport={"width": w, "height": h},
                                      device_scale_factor=2 if vp_name == "mobile" else 1,
                                      locale="en-US")
            page = ctx.new_page()
            errors = []
            page.on("console", lambda m: errors.append(m.text)
                    if m.type in ("error", "warning") else None)
            page.on("pageerror", lambda e: errors.append("PAGEERROR " + str(e)))

            for pg in PAGES:
                url = f"file://{ROOT}/{pg}?lang={lang}"
                errors.clear()
                page.goto(url, wait_until="load")
                page.wait_for_timeout(700)
                # Scroll the whole page so lazy-loaded images are decoded
                page.evaluate("""async()=>{
                    const step = window.innerHeight;
                    for (let y = 0; y < document.body.scrollHeight; y += step) {
                        window.scrollTo(0, y);
                        await new Promise(r => setTimeout(r, 90));
                    }
                    window.scrollTo(0, document.body.scrollHeight);
                    await new Promise(r => setTimeout(r, 600));
                }""")
                page.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('is-visible'))")
                try:
                    page.wait_for_function(
                        "()=>Array.from(document.images).every(i=>i.complete && i.naturalWidth>0)",
                        timeout=12000)
                except Exception:
                    bad_imgs = page.evaluate(
                        "()=>Array.from(document.images).filter(i=>!i.complete||!i.naturalWidth)"
                        ".map(i=>(i.currentSrc||i.src).split('/').pop()+' loading='+i.loading)")
                    problems.append(f"{pg}-{lang}-{vp_name}: image failed to load {bad_imgs}")
                page.evaluate("window.scrollTo(0,0)")
                page.wait_for_timeout(350)

                tag = f"{pg.replace('.html','')}-{lang}-{vp_name}"

                # --- direction / lang -------------------------------------
                attrs = page.evaluate("()=>({lang:document.documentElement.lang,"
                                      "dir:document.documentElement.dir,"
                                      "title:document.title})")
                expected_dir = "rtl" if lang == "ar" else "ltr"
                if attrs["lang"] != lang or attrs["dir"] != expected_dir:
                    problems.append(f"{tag}: wrong lang/dir {attrs}")
                if not attrs["title"] or attrs["title"] == "German Global Accounting LLC":
                    problems.append(f"{tag}: meta title not localised ({attrs['title']!r})")

                # --- horizontal overflow ----------------------------------
                overflow = page.evaluate("""(vw)=>{
                    const bad=[];
                    document.querySelectorAll('body *').forEach(el=>{
                      const r=el.getBoundingClientRect();
                      if(r.width===0&&r.height===0) return;
                      if(r.right>vw+1.5||r.left<-1.5){
                        const cs=getComputedStyle(el);
                        if(cs.position==='fixed') return;
                        bad.push(el.tagName.toLowerCase()+'.'+(el.className&&el.className.baseVal===undefined?String(el.className).split(' ')[0]:'')+
                                 ' L'+Math.round(r.left)+' R'+Math.round(r.right));
                      }
                    });
                    return {doc: document.documentElement.scrollWidth, bad: bad.slice(0,6)};
                }""", w)
                if overflow["doc"] > w + 1:
                    problems.append(f"{tag}: page scrollWidth {overflow['doc']} > {w} :: {overflow['bad']}")

                # --- untranslated / leaked text ---------------------------
                text = page.evaluate("()=>document.body.innerText")
                raw_keys = re.findall(r"\b(?:svc_|form_|why\d|process\d|addl\d|pricing_|about_|"
                                      r"contact_|hero_|trust_|service\d|meta_|nav_|footer_)\w*", text)
                if raw_keys:
                    problems.append(f"{tag}: untranslated keys on screen {sorted(set(raw_keys))[:6]}")

                # --- text / background contrast ---------------------------
                # Catches navy-on-navy and similar invisible text, and doubles
                # as a WCAG AA check against the real rendered colours.
                low = page.evaluate(CONTRAST_JS)
                if low:
                    problems.append(f"{tag}: low contrast {low}")

                leaks = check_leak(lang, text)
                if leaks:
                    problems.append(f"{tag}: language leak {sorted(set(leaks))[:8]}")

                real_errors = [e for e in errors if "i18n" in e or "PAGEERROR" in e]
                if real_errors:
                    problems.append(f"{tag}: console {real_errors[:4]}")

                page.screenshot(path=f"{SHOT_DIR}/{tag}.png", full_page=True)

            ctx.close()
    browser.close()

print("=" * 66)
if problems:
    print(f"{len(problems)} PROBLEM(S):")
    for pr in problems:
        print("  •", pr)
else:
    print("ALL CHECKS PASSED")
print("=" * 66)
