#!/usr/bin/env python3
"""
Generates all seven HTML pages (five site pages + two legal pages) from shared partials.

The header, drawer, footer and flag sprite are defined once here so they
cannot drift apart between pages — the previous version had five hand-kept
copies, which is how the language switcher ended up inconsistent.

Output is plain, readable static HTML with no build step required to run it.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

import re

OUT = "."
MAPS = "https://maps.app.goo.gl/wHXvxcAbBTNFSUDJ6"
EMAIL = "Germanglobalacc@gmail.com"
PHONE_HREF = "+971508821960"
PHONE_TEXT = "+971 50 882 1960"

# --------------------------------------------------------------------------
# Icons (inline, currentColor)
# --------------------------------------------------------------------------
ARROW = ('<svg class="arw" width="16" height="16" viewBox="0 0 16 16" fill="none" '
         'stroke="currentColor" stroke-width="1.6" aria-hidden="true">'
         '<path d="M2.5 8h11M9 3.5 13.5 8 9 12.5"/></svg>')
CHECK = ('<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" '
         'aria-hidden="true"><path d="M13.5 4.5 6.2 11.8 2.5 8.1"/></svg>')
WA_ICON = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
           '<path d="M17.5 14.4c-.3-.1-1.7-.8-2-.9-.3-.1-.5-.1-.7.1-.2.3-.7.9-.9 1.1-.2.2-.3.2-.6.1'
           '-.3-.1-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6.1-.1.3-.3.4-.5.1-.2.2-.3.3-.5'
           '.1-.2 0-.4 0-.5C10.8 9.2 10.3 8 10.1 7.5c-.2-.5-.4-.4-.6-.4h-.5c-.2 0-.5.1-.7.3-.2.3-.9.9'
           '-.9 2.1s1 2.5 1.1 2.6c.1.2 2 3 4.8 4.2.7.3 1.2.5 1.6.6.7.2 1.3.2 1.8.1.5-.1 1.7-.7 1.9-1.4'
           '.2-.7.2-1.2.2-1.3-.1-.1-.3-.2-.6-.3z"/>'
           '<path d="M12 2C6.5 2 2 6.5 2 12c0 1.9.5 3.6 1.4 5.1L2 22l5.1-1.3c1.4.8 3.1 1.2 4.9 1.2 5.5 0 '
           '10-4.5 10-10S17.5 2 12 2zm0 18.2c-1.6 0-3.1-.4-4.4-1.2l-.3-.2-3.3.9.9-3.2-.2-.3C3.9 14.6 3.5 '
           '13.3 3.5 12 3.5 7.3 7.3 3.5 12 3.5S20.5 7.3 20.5 12 16.7 20.2 12 20.2z"/></svg>')
PHONE_ICON = ('<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
              'stroke-width="1.7" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1'
              '-8.6-3.1 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3.1-8.7A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 '
              '.3 2 .7 2.9a2 2 0 0 1-.4 2.1L8.1 9.9a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.4c.9.4 1.9.6 2.9.7'
              'a2 2 0 0 1 1.7 2.1z"/></svg>')
MAIL_ICON = ('<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
             'stroke-width="1.7" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/>'
             '<path d="m2 7 10 6 10-6"/></svg>')
PIN_ICON = ('<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="1.5" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/>'
            '<circle cx="12" cy="10" r="3"/></svg>')
GLOBE_ICON = ('<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
              'stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/>'
              '<path d="M12 3a14 14 0 0 1 0 18 14 14 0 0 1 0-18z"/></svg>')

ICON_BOOK = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">'
             '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>'
             '<path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>')
ICON_PERCENT = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">'
                '<circle cx="7" cy="7" r="3.2"/><circle cx="17" cy="17" r="3.2"/><path d="M18 6 6 18"/></svg>')
ICON_BRIEFCASE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">'
                   '<rect x="3" y="7.5" width="18" height="12" rx="2"/><path d="M8 7.5V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v1.5"/>'
                   '<path d="M3 12.5h18"/></svg>')
ICON_HEART = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
              'stroke-linejoin="round" aria-hidden="true"><path d="M12 20.5s-7.5-4.6-9.2-9.6C1.6 7.4 3.6 4.5 6.7 4.5c2 0 3.6 1 5.3 3 1.7-2 3.3-3 5.3-3 3.1 0 5.1 2.9 3.9 6.4-1.7 5-9.2 9.6-9.2 9.6z"/></svg>')
GLOBE_SM = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
            'aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a14 14 0 0 1 0 18 14 14 0 0 1 0-18z"/></svg>')
ICON_TARGET = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
               'aria-hidden="true"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.2" fill="currentColor"/></svg>')
ICON_CHART = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">'
              '<path d="M4 20V10M12 20V4M20 20v-7"/></svg>')

MERIDIAN = ('<svg class="meridian{extra}" viewBox="0 0 400 400" aria-hidden="true" focusable="false">'
            '<circle cx="200" cy="200" r="150"/>'
            '<ellipse cx="200" cy="200" rx="58" ry="150"/>'
            '<ellipse cx="200" cy="200" rx="108" ry="150"/>'
            '<line x1="50" y1="200" x2="350" y2="200"/>'
            '<line x1="72" y1="128" x2="328" y2="128"/>'
            '<line x1="72" y1="272" x2="328" y2="272"/>'
            '<circle class="m-gold" cx="200" cy="200" r="176"/></svg>')

FLAG_SPRITE = """
<svg style="position:absolute;width:0;height:0;overflow:hidden" aria-hidden="true" focusable="false">
  <defs>
    <!-- United Kingdom -->
    <symbol id="flag-en" viewBox="0 0 60 30" preserveAspectRatio="xMidYMid slice">
      <clipPath id="uk-a"><path d="M0 0v30h60V0z"/></clipPath>
      <clipPath id="uk-b"><path d="M30 15h30v15zv15H30zH0V15zV0h30z"/></clipPath>
      <g clip-path="url(#uk-a)">
        <path d="M0 0v30h60V0z" fill="#012169"/>
        <path d="M0 0 60 30M60 0 0 30" stroke="#fff" stroke-width="6"/>
        <path d="M0 0 60 30M60 0 0 30" clip-path="url(#uk-b)" stroke="#C8102E" stroke-width="4"/>
        <path d="M30 0v30M0 15h60" stroke="#fff" stroke-width="10"/>
        <path d="M30 0v30M0 15h60" stroke="#C8102E" stroke-width="6"/>
      </g>
    </symbol>
    <!-- Germany -->
    <symbol id="flag-de" viewBox="0 0 5 3" preserveAspectRatio="xMidYMid slice">
      <path d="M0 0h5v3H0z" fill="#000"/>
      <path d="M0 1h5v2H0z" fill="#D00"/>
      <path d="M0 2h5v1H0z" fill="#FFCE00"/>
    </symbol>
    <!-- United Arab Emirates -->
    <symbol id="flag-ar" viewBox="0 0 12 6" preserveAspectRatio="xMidYMid slice">
      <path d="M0 0h12v2H0z" fill="#00732F"/>
      <path d="M0 2h12v2H0z" fill="#fff"/>
      <path d="M0 4h12v2H0z" fill="#000"/>
      <path d="M0 0h3v6H0z" fill="#FF0000"/>
    </symbol>
  </defs>
</svg>
"""

NAV_ITEMS = [
    ("index.html", "nav_home", "home"),
    ("about.html", "nav_about", "about"),
    ("services.html", "nav_services", "services"),
    ("pricing.html", "nav_pricing", "pricing"),
    ("contact.html", "nav_contact", "contact"),
]

# Native language names are deliberately shown in their own language —
# that is the universal convention for a language picker, not a language mix.
LANG_OPTS = [("en", "English"), ("de", "Deutsch"), ("ar", "العربية")]


def flag(lang, cls="flag"):
    return (f'<svg class="{cls}" viewBox="0 0 24 16" preserveAspectRatio="none" aria-hidden="true">'
            f'<use href="#flag-{lang}" width="24" height="16"/></svg>')


LANG_SHORT = {"en": "EN", "de": "DE", "ar": "ع"}


def lang_switch():
    """Segmented language control with a sliding pill (positioned by site.js).

    Each button carries the language's own name as its accessible label, since
    the visible text is only the short code.
    """
    btns = "\n".join(
        f'''        <button type="button" class="lang-btn" data-lang="{code}" aria-current="{'true' if code == 'en' else 'false'}" lang="{code}" aria-label="{native}">
          {flag(code)}<span class="lang-code">{LANG_SHORT[code]}</span>
        </button>'''
        for code, native in LANG_OPTS)
    return f'''      <div class="lang" role="group" data-i18n="lang_choose" data-i18n-attr="aria-label">
        <span class="lang-pill" aria-hidden="true"></span>
{btns}
      </div>'''


def header(active):
    links = "\n".join(
        f'''          <li><a class="nav-link" href="{href}" data-i18n="{key}"'''
        f'''{' aria-current="page"' if page == active else ''}>{key}</a></li>'''
        for href, key, page in NAV_ITEMS)
    return f'''<header class="site-header" id="siteHeader">
  <div class="nav-wrap container">
    <a href="index.html" class="brand" aria-label="German Global Accounting LLC">
      <img src="assets/img/logo-mark.png" alt="German Global Accounting LLC" width="392" height="260">
    </a>

    <nav class="nav-primary" aria-label="Main">
      <ul>
{links}
      </ul>
    </nav>

    <div class="nav-actions">
{lang_switch()}

      <a class="btn btn-primary nav-cta-desktop" data-wa="consult" href="https://wa.me/971508821960"
         target="_blank" rel="noopener" data-i18n="nav_cta">Book a Consultation</a>

      <button type="button" class="nav-toggle" id="navToggle" aria-expanded="false" aria-controls="mobileNav"
              data-i18n="nav_menu_open" data-i18n-attr="aria-label">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</header>

<div class="nav-scrim" id="navScrim" hidden-aria></div>

<aside class="mobile-nav" id="mobileNav" aria-hidden="true" aria-label="Menu">
  <div class="mobile-nav-head">
    <img src="assets/img/logo-mark.png" alt="German Global Accounting LLC" width="392" height="260">
    <button type="button" class="nav-toggle" id="navClose" aria-expanded="true"
            data-i18n="nav_menu_close" data-i18n-attr="aria-label">
      <span></span><span></span><span></span>
    </button>
  </div>
  <div class="mobile-nav-body">
    <ul class="mobile-nav-links">
{chr(10).join(f'      <li><a href="{href}"{" aria-current=" + chr(34) + "page" + chr(34) if page == active else ""}><span class="index-num">0{i+1}</span><span data-i18n="{key}">{key}</span></a></li>' for i, (href, key, page) in enumerate(NAV_ITEMS))}
    </ul>

    <div>
      <p class="mobile-lang-label" data-i18n="lang_label">Language</p>
      <div class="mobile-lang">
{chr(10).join(f'        <button type="button" data-lang="{c}" aria-current="{"true" if c == "en" else "false"}" lang="{c}">{flag(c)}<span>{n}</span></button>' for c, n in LANG_OPTS)}
      </div>
    </div>

    <div class="mobile-nav-foot">
      <a class="btn btn-primary" data-wa="consult" href="https://wa.me/971508821960" target="_blank" rel="noopener" data-i18n="nav_cta">Book a Consultation</a>
      <a class="btn btn-outline" href="contact.html" data-i18n="nav_contact">Contact</a>
    </div>
  </div>
</aside>
'''


def footer():
    services = "\n".join(
        f'          <li><a href="services.html#{anchor}" data-i18n="{key}">{key}</a></li>'
        for anchor, key in [("bookkeeping", "service1_title"), ("vat", "service2_title"),
                            ("corporate-tax", "service3_title"), ("business-support", "service4_title")])
    nav = "\n".join(
        f'          <li><a href="{href}" data-i18n="{key}">{key}</a></li>'
        for href, key, _ in NAV_ITEMS)
    langs = "\n".join(
        f'        <button type="button" data-lang="{c}" aria-current="{"true" if c == "en" else "false"}" lang="{c}">{flag(c)}<span>{n}</span></button>'
        for c, n in LANG_OPTS)
    return f'''<footer class="site-footer">
  {MERIDIAN.format(extra=" meridian--start")}
  <div class="container footer-top">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="assets/img/logo-plate.png" alt="German Global Accounting LLC" width="591" height="372">
        <p class="footer-tagline" data-i18n="footer_tagline">Bookkeeping and tax consultancy.</p>
      </div>

      <div class="footer-col">
        <h3 data-i18n="footer_nav_label">Navigate</h3>
        <ul>
{nav}
        </ul>
      </div>

      <div class="footer-col">
        <h3 data-i18n="footer_services_label">Services</h3>
        <ul>
{services}
        </ul>
      </div>

      <div class="footer-col">
        <h3 data-i18n="footer_contact_label">Contact</h3>
        <address data-i18n="contact_address">Muwaihat 1, Al Tallah Road<br>Ajman, United Arab Emirates</address>
        <ul>
          <li><a data-wa="consult" href="https://wa.me/971508821960" target="_blank" rel="noopener">WhatsApp</a></li>
          <li><a href="{MAPS}" target="_blank" rel="noopener" data-i18n="footer_directions">Get Directions</a></li>
        </ul>
      </div>
    </div>
  </div>

  <div class="container">
    <div class="footer-bottom">
      <p>© <span data-year>2026</span> German Global Accounting LLC. <span data-i18n="footer_rights">All rights reserved.</span></p>
      <div class="footer-legal">
        <a href="privacy.html" data-i18n="footer_privacy">Privacy Policy</a>
        <a href="impressum.html" data-i18n="footer_impressum">Impressum</a>
      </div>
      <div class="footer-lang">
        <span class="lbl" data-i18n="footer_lang_label">Language</span>
{langs}
      </div>
    </div>
  </div>
</footer>

<button type="button" class="to-top" id="toTop" data-i18n="to_top" data-i18n-attr="aria-label" aria-label="Back to top">
  <svg viewBox="0 0 44 44" aria-hidden="true" focusable="false">
    <circle class="tt-track" cx="22" cy="22" r="19"/>
    <circle class="tt-fill" cx="22" cy="22" r="19" pathLength="100"/>
    <path class="tt-arrow" d="M22 28V16M16.5 21.5 22 16l5.5 5.5"/>
  </svg>
</button>

<a class="wa-float" data-wa="consult" href="https://wa.me/971508821960" target="_blank" rel="noopener"
   data-i18n="wa_label" data-i18n-attr="aria-label">{WA_ICON}</a>

<script src="assets/i18n.js" defer></script>
<script src="assets/site.js" defer></script>
</div><!-- /.site-shell -->
</body>
</html>
'''


def cta_band():
    return f'''  <section class="section section--navy cta-band">
    {MERIDIAN.format(extra="")}
    <div class="container">
      <div class="cta-inner">
        <p class="eyebrow" data-i18n="contact_eyebrow">Contact</p>
        <h2 data-i18n="cta_heading">You Focus on Your Business. We Take Care of Your Finances.</h2>
        <p data-i18n="cta_sub">Everything you need in one place.</p>
        <div class="btn-group">
          <a class="btn btn-primary" href="contact.html" data-i18n="cta_button">Contact Us</a>
          <a class="btn btn-on-navy" data-wa="consult" href="https://wa.me/971508821960" target="_blank" rel="noopener" data-i18n="cta_button_wa">Message on WhatsApp</a>
        </div>
        <p class="cta-note" data-i18n="cta_note">Contact us for a non-binding initial consultation.</p>
      </div>
    </div>
  </section>
'''


def head(title_key, desc_key, static_title=None, static_desc=None, html_lang="en", extra=""):
    """Document head + opening of the page shell.

    Normal pages pass i18n keys (the language engine fills title/description).
    The two legal pages carry static text instead, so they pass static_title /
    static_desc and no data-*-key attributes.
    """
    if title_key:
        html_attrs = f'lang="en" dir="ltr" data-title-key="{title_key}" data-desc-key="{desc_key}"'
        title = "German Global Accounting LLC"
        desc = "Bookkeeping, VAT and Corporate Tax support for businesses in Ajman, Dubai and across the UAE."
    else:
        html_attrs = f'lang="{html_lang}" dir="ltr"'
        title, desc = static_title, static_desc
    return f'''<!DOCTYPE html>
<html {html_attrs}>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0A1A26">
<link rel="icon" href="assets/img/favicon.png" type="image/png">
{extra}<link rel="preload" href="assets/fonts/Inter-normal-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,500;1,9..144,600&display=swap" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,500;1,9..144,600&display=swap"></noscript>
<script>document.documentElement.classList.add("js")</script>
<link rel="stylesheet" href="assets/styles.css">
</head>
<body>
<a class="skip-link" href="#main" data-i18n="skip_link">Skip to content</a>
<div class="site-shell">
{FLAG_SPRITE}'''


# --------------------------------------------------------------------------
# PAGE: HOME
# --------------------------------------------------------------------------
SERVICES = [
    ("bookkeeping", "service1_title", "service1_desc"),
    ("vat", "service2_title", "service2_desc"),
    ("corporate-tax", "service3_title", "service3_desc"),
    ("business-support", "service4_title", "service4_desc"),
]


HERO_PRELOAD = ('<link rel="preload" as="image" href="assets/img/hero-sm.jpg" media="(max-width: 899px)" fetchpriority="high">\n'
                '<link rel="preload" as="image" href="assets/img/hero-lg.jpg" media="(min-width: 900px)" fetchpriority="high">\n')


def home():
    icons = {"bookkeeping": ICON_BOOK, "vat": ICON_PERCENT,
             "corporate-tax": ICON_BRIEFCASE, "business-support": ICON_CHART}
    cards = "\n".join(f'''        <a class="card reveal" href="services.html#{anchor}">
          <span class="card-glare" aria-hidden="true"></span>
          <span class="card-ic">{icons[anchor]}</span>
          <h3 data-i18n="{tkey}">{tkey}</h3>
          <p data-i18n="{dkey}">{dkey}</p>
          <span class="card-go" aria-hidden="true">{ARROW.replace('class="arw" ', '')}</span>
        </a>''' for anchor, tkey, dkey in SERVICES)

    why_items = "\n".join(f'''          <li class="why-item reveal">
            <span class="n">0{i}</span>
            <h3 data-i18n="why{i}_title">why{i}_title</h3>
            <p data-i18n="why{i}_desc">why{i}_desc</p>
          </li>''' for i in range(1, 6))

    process = "\n".join(f'''        <div class="process-step reveal">
          <div class="n">0{i}</div>
          <h3 data-i18n="process{i}_title">process{i}_title</h3>
          <p data-i18n="process{i}_desc">process{i}_desc</p>
        </div>''' for i in range(1, 4))

    chips = "\n".join(f'          <li data-i18n="addl{i}_title">addl{i}_title</li>' for i in range(1, 5))

    return head("meta_title_home", "meta_desc_home", extra=HERO_PRELOAD) + header("home") + f'''
<main id="main">

  <!-- ================= HERO ================= -->
  <section class="hero-v2">
    <div class="container">
      <div class="hero-v2-card">
        <picture>
          <source media="(min-width: 900px)" srcset="assets/img/hero-lg.jpg">
          <img src="assets/img/hero-sm.jpg" alt="" width="640" height="959" fetchpriority="high" decoding="async">
        </picture>

        <div class="hero-v2-body">
          <div class="hero-v2-copy">
            <span class="hero-v2-tag"><span class="dot"></span><span data-i18n="hero_eyebrow">Bookkeeping &amp; Tax Consultancy &middot; Ajman, UAE</span></span>
            <h1 data-i18n="hero_headline">Professional financial solutions</h1>
            <p class="hero-v2-sub" data-i18n="hero_sub">Accounting, VAT &amp; Corporate Tax.</p>

            <ul class="hero-points">
              <li><span class="hp-ic">{ICON_HEART}</span><span data-i18n="hero_pt1">Personalised Service</span></li>
              <li><span class="hp-ic">{GLOBE_SM}</span><span data-i18n="hero_pt2">German &amp; UAE Expertise</span></li>
              <li><span class="hp-ic">{ICON_TARGET}</span><span data-i18n="hero_pt3">Business-Focused Advice</span></li>
            </ul>

            <div class="btn-group hero-ctas">
              <a class="btn btn-primary btn-pill" data-wa="consult" href="https://wa.me/971508821960" target="_blank" rel="noopener"><span data-i18n="hero_cta_primary">Book a Consultation</span>{ARROW}</a>
              <a class="btn btn-on-navy btn-pill" href="services.html"><span data-i18n="hero_cta_secondary">Explore Services</span>{ARROW}</a>
            </div>
          </div>
        </div>

        <div class="hero-v2-bottom">
          <div class="hero-v2-tags">
            <span><b>+</b><span data-i18n="hero_tag1">Bookkeeping</span></span>
            <span><b>+</b><span data-i18n="hero_tag2">VAT</span></span>
            <span><b>+</b><span data-i18n="hero_tag3">Corporate Tax</span></span>
            <span><b>+</b><span data-i18n="hero_tag4">Business Support</span></span>
          </div>
          <p class="hero-v2-meta">
            <span class="hero-chip"><b data-i18n="hero_meta_office_label">Office</b><span data-i18n="hero_meta_office">Muwaihat 1, Al Tallah Road, Ajman</span></span>
            <span class="hero-chip"><b data-i18n="hero_meta_online_label">Or online</b><span data-i18n="hero_meta_online">Anywhere in the UAE</span></span>
          </p>
        </div>
      </div>
    </div>
  </section>


  <!-- ================= SERVICES ================= -->
  <section class="section" id="services">
    <div class="container">
      <div class="section-head section-head--split">
        <div>
          <p class="eyebrow" data-i18n="services_eyebrow">Services</p>
          <h2 data-i18n="services_heading">Everything your finances need, in one place</h2>
        </div>
        <p data-i18n="services_sub">Comprehensive solutions tailored to your business.</p>
      </div>

      <div class="cards">
{cards}
      </div>

      <div class="ledger-foot">
        <a class="link-arrow" href="services.html"><span data-i18n="services_all_link">View all services</span>{ARROW}</a>
      </div>
    </div>
  </section>

  <!-- ================= WHY CHOOSE US ================= -->
  <section class="section section--navy">
    {MERIDIAN.format(extra="")}
    <div class="container">
      <div class="why-grid">
        <div>
          <figure class="why-figure reveal">
            <img src="assets/img/tower-tall.jpg" alt="" width="1000" height="1250" loading="lazy" decoding="async">
          </figure>
          <p class="why-quote" data-i18n="why_tagline">Personal. Professional. Reliable.</p>
        </div>

        <div>
          <div class="section-head" style="margin-block-end:0">
            <p class="eyebrow" data-i18n="why_eyebrow">Why choose us</p>
            <h2 data-i18n="why_heading">A partner, not a processor</h2>
            <p data-i18n="why_intro">We stand for clear communication.</p>
          </div>
          <ul class="why-list">
{why_items}
          </ul>
        </div>
      </div>
    </div>
  </section>

  <!-- ================= PROCESS ================= -->
  <section class="section">
    <div class="container">
      <div class="section-head section-head--split">
        <div>
          <p class="eyebrow" data-i18n="process_eyebrow">How we work</p>
          <h2 data-i18n="process_heading">How We Work Together</h2>
        </div>
        <p data-i18n="process_sub">A clear path from first conversation to ongoing support.</p>
      </div>
      <div class="process-grid">
        <div class="process-beam" aria-hidden="true"></div>
{process}
      </div>
    </div>
  </section>

  <!-- ================= BUSINESS SUPPORT ================= -->
  <section class="section section--paper2">
    <div class="container">
      <div class="split split--wide-text">
        <figure class="split-figure reveal">
          <picture>
            <source media="(min-width: 900px)" srcset="assets/img/consult-lg.jpg">
            <img src="assets/img/consult-sm.jpg" alt="" width="1100" height="825" loading="lazy" decoding="async">
          </picture>
        </figure>

        <div>
          <p class="eyebrow" data-i18n="support_eyebrow">Business support</p>
          <h2 data-i18n="support_heading">Beyond the books</h2>
          <div class="prose" style="margin-block-start:1.25rem">
            <p data-i18n="support_text">Good financial information is more than numbers.</p>
          </div>
          <ul class="chips">
{chips}
          </ul>
          <p style="margin-block-start:1.75rem">
            <a class="link-arrow" href="services.html#business-support"><span data-i18n="support_link">See how we support your business</span>{ARROW}</a>
          </p>
        </div>
      </div>
    </div>
  </section>

{cta_band()}
</main>

''' + footer()


# --------------------------------------------------------------------------
# PAGE: ABOUT
# --------------------------------------------------------------------------
def about():
    return head("meta_title_about", "meta_desc_about") + header("about") + f'''
<main id="main">

  <section class="page-head page-head--light">
    <div class="container">
      <div class="page-head-inner">
        <p class="eyebrow" data-i18n="about_eyebrow">About Us</p>
        <h1 data-i18n="about_h1">Experience, Expertise &amp; Personal Support</h1>
        <p data-i18n="about_intro">We understand the challenges businesses face in the UAE.</p>
      </div>
    </div>
  </section>

  <!-- Background / Approach -->
  <section class="section section--tight">
    <div class="container">
      <div class="about-cols">
        <div class="about-col reveal">
          <span class="label" data-i18n="about_bg_label">01 — Background</span>
          <h2 data-i18n="about_bg_h2">Our Background</h2>
          <div class="prose"><p data-i18n="about_bg_p">Our team has several years of experience.</p></div>
        </div>
        <div class="about-col reveal">
          <span class="label" data-i18n="about_approach_label">02 — Approach</span>
          <h2 data-i18n="about_approach_h2">Our Approach</h2>
          <div class="prose"><p data-i18n="about_approach_p">Our goal is reliable, long-term support.</p></div>
        </div>
      </div>
    </div>
  </section>

  <!-- Editorial image break -->
  <section class="section section--tight section--paper2">
    <div class="container">
      <div class="split split--flip">
        <figure class="split-figure reveal">
          <picture>
            <source media="(min-width: 900px)" srcset="assets/img/consult-lg.jpg">
            <img src="assets/img/consult-sm.jpg" alt="" width="1100" height="825" loading="lazy" decoding="async">
          </picture>
        </figure>
        <div>
          <p class="eyebrow" data-i18n="about_time_eyebrow">Your time</p>
          <h2 data-i18n="about_time_h2">More Time for Your Core Business</h2>
          <div class="prose" style="margin-block-start:1.5rem">
            <p><strong data-i18n="about_time_p1">Your time should be invested in your business.</strong></p>
            <p data-i18n="about_time_p2">Especially during the start-up phase…</p>
          </div>
        </div>
      </div>

      <div class="split" style="margin-block-start:clamp(2.5rem, 2rem + 3vw, 4.5rem)">
        <div class="prose">
          <p data-i18n="about_time_p3">We take care of defined areas of your financial processes.</p>
          <p data-i18n="about_time_p4">Established businesses can also benefit.</p>
        </div>
        <div class="goal-card reveal">
          {MERIDIAN.format(extra="")}
          <span class="goal-label" data-i18n="about_time_goal_label">Our Goal</span>
          <p data-i18n="about_time_goal">You stay on top of your numbers.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Location -->
  <section class="section">
    <div class="container">
      <div class="section-head">
        <p class="eyebrow" data-i18n="about_location_eyebrow">Where we work</p>
        <h2 data-i18n="about_location_h2">Ajman, and Online</h2>
        <p data-i18n="about_location_p">Visit our office or work with us online.</p>
      </div>

      <div class="place-grid">
        <div class="place-card reveal">
          <div class="ico">{PIN_ICON}</div>
          <h3 data-i18n="about_location_visit">Visit the office</h3>
          <p data-i18n="about_location_visit_desc">Muwaihat 1, Al Tallah Road, Ajman.</p>
          <a class="link-arrow" href="{MAPS}" target="_blank" rel="noopener"><span data-i18n="contact_directions">Get Directions</span>{ARROW}</a>
        </div>
        <div class="place-card reveal">
          <div class="ico">{GLOBE_ICON}</div>
          <h3 data-i18n="about_location_remote">Work with us online</h3>
          <p data-i18n="about_location_remote_desc">Services can also be provided online.</p>
          <a class="link-arrow" href="contact.html"><span data-i18n="nav_contact">Contact</span>{ARROW}</a>
        </div>
      </div>
    </div>
  </section>

{cta_band()}
</main>

''' + footer()


# --------------------------------------------------------------------------
# PAGE: SERVICES
# --------------------------------------------------------------------------
SVC_DETAIL = [
    ("bookkeeping", "service1_title", "svc_book_intro", "svc_book", 10, "svc_book_closing", "svc-book.jpg", ICON_BOOK),
    ("vat", "service2_title", "svc_vat_intro", "svc_vat", 5, "svc_vat_closing", "svc-vat.jpg", ICON_PERCENT),
    ("corporate-tax", "service3_title", "svc_ctax_intro", "svc_ctax", 7, "svc_ctax_closing", "svc-ctax.jpg", ICON_BRIEFCASE),
    ("business-support", "service4_title", "svc_bsupport_intro", "svc_bsupport", 8, None, "svc-support.jpg", ICON_CHART),
]


def services():
    index = "\n".join(
        f'        <a href="#{anchor}"><span class="index-num">0{i + 1}</span><span data-i18n="{tkey}">{tkey}</span></a>'
        for i, (anchor, tkey, _, _, _, _, _, _) in enumerate(SVC_DETAIL))

    blocks = []
    for i, (anchor, tkey, intro, prefix, count, closing, photo, icon) in enumerate(SVC_DETAIL):
        items = "\n".join(
            f'            <li>{CHECK}<span data-i18n="{prefix}_item{n}">{prefix}_item{n}</span></li>'
            for n in range(1, count + 1))
        closing_html = (f'''
          <p class="svc-closing" data-i18n="{closing}">{closing}</p>''' if closing else "")
        blocks.append(f'''      <article class="svc-detail reveal" id="{anchor}">
        <picture class="svc-detail-bg">
          <img src="assets/img/{photo}" alt="" width="1200" height="1000" loading="lazy" decoding="async">
        </picture>
        <div class="svc-detail-inner">
          <div class="svc-detail-head">
            <span class="svc-icon">{icon}</span>
            <span class="index-num">0{i + 1}</span>
            <h2 data-i18n="{tkey}">{tkey}</h2>
            <p class="svc-intro" data-i18n="{intro}">{intro}</p>
          </div>
          <div>
            <p class="svc-includes-label" data-i18n="svc_includes_label">What this includes</p>
            <ul class="svc-list">
{items}
            </ul>{closing_html}
            <div class="svc-cta-row">
              <a class="btn btn-gold-solid" data-wa="consult" href="https://wa.me/971508821960" target="_blank" rel="noopener">
                <span data-i18n="svc_cta_book">Book a call about this</span>{ARROW}
              </a>
            </div>
          </div>
        </div>
      </article>''')

    addl = "\n".join(f'''        <div class="addl-card reveal">
          <span class="n">0{i}</span>
          <h3 data-i18n="addl{i}_title">addl{i}_title</h3>
          <p data-i18n="addl{i}_desc">addl{i}_desc</p>
        </div>''' for i in range(1, 5))

    return head("meta_title_services", "meta_desc_services") + header("services") + f'''
<main id="main">

  <section class="page-head section--navy">
    {MERIDIAN.format(extra="")}
    <div class="container">
      <div class="page-head-inner">
        <p class="eyebrow" data-i18n="services_page_eyebrow">Services</p>
        <h1 data-i18n="services_page_h1">Accounting, Tax &amp; Financial Business Solutions</h1>
        <p data-i18n="services_page_intro">We combine accounting, tax compliance and business support.</p>
      </div>
    </div>
    <div class="page-head-band">
      <img src="assets/img/glass-band.jpg" alt="" width="1600" height="435" loading="lazy" decoding="async">
    </div>
  </section>

  <nav class="svc-index" aria-label="Services">
    <div class="container">
      <div class="svc-index-inner">
        <span class="svc-index-label" data-i18n="services_index_label">On this page</span>
{index}
      </div>
    </div>
  </nav>

  <section class="section--tight">
    <div class="container">
{chr(10).join(blocks)}
    </div>
  </section>

  <section class="section section--sand">
    <div class="container">
      <div class="section-head">
        <p class="eyebrow" data-i18n="svc_addl_eyebrow">Also available</p>
        <h2 data-i18n="svc_addl_heading">Additional Services</h2>
      </div>
      <div class="addl-grid">
{addl}
      </div>
    </div>
  </section>

{cta_band()}
</main>

''' + footer()


# --------------------------------------------------------------------------
# PAGE: PRICING
# --------------------------------------------------------------------------
def pricing():
    factors = "\n".join(f'''        <div class="factor reveal">
          <span class="n">0{i}</span>
          <h3 data-i18n="pricing_factor{i}_title">pricing_factor{i}_title</h3>
          <p data-i18n="pricing_factor{i}_desc">pricing_factor{i}_desc</p>
        </div>''' for i in range(1, 4))

    return head("meta_title_pricing", "meta_desc_pricing") + header("pricing") + f'''
<main id="main">

  <section class="page-head section--navy">
    {MERIDIAN.format(extra="")}
    <div class="container">
      <div class="page-head-inner">
        <p class="eyebrow" data-i18n="pricing_eyebrow">Pricing</p>
        <h1 data-i18n="pricing_h1">Fair Pricing. Transparent Services. Personal Support.</h1>
        <p data-i18n="pricing_intro">Tailored to the individual needs of your business.</p>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="section-head section-head--split">
        <div>
          <p class="eyebrow" data-i18n="pricing_tailored_eyebrow">Our approach</p>
          <h2 data-i18n="pricing_tailored_h2">Tailored Solutions for Your Business</h2>
        </div>
        <p data-i18n="pricing_tailored_p">Every business has different structures and requirements.</p>
      </div>

      <figure class="pricing-feature reveal">
        <img src="assets/img/pricing-team-sm.jpg" srcset="assets/img/pricing-team-sm.jpg 760w, assets/img/pricing-team.jpg 1400w" sizes="(min-width: 1320px) 1200px, calc(100vw - 2.5rem)" alt="UAE business consultation" width="1400" height="788" loading="lazy" decoding="async" data-i18n="pricing_image_alt" data-i18n-attr="alt">
      </figure>

      <div class="factor-grid">
{factors}
      </div>
    </div>
  </section>

  <section class="section section--tight">
    <div class="container">
      <div class="quote-panel reveal">
        {MERIDIAN.format(extra="")}
        <div class="quote-panel-inner">
          <p class="eyebrow" data-i18n="contact_eyebrow">Contact</p>
          <h2 data-i18n="pricing_panel_title">Request Your Personal Price List</h2>
          <p data-i18n="pricing_panel_text">We are happy to send you our current price list.</p>
          <div class="btn-group">
            <a class="btn btn-primary" data-wa="price" href="https://wa.me/971508821960" target="_blank" rel="noopener" data-i18n="pricing_cta_button">Request Price List on WhatsApp</a>
            <a class="btn btn-on-navy" href="contact.html" data-i18n="pricing_cta_alt">Or send us a message</a>
          </div>
          <p class="pricing-tagline" data-i18n="pricing_tagline">Fair Pricing · Clear Services · Personal Service</p>
        </div>
      </div>
    </div>
  </section>

{cta_band()}
</main>

''' + footer()


# --------------------------------------------------------------------------
# PAGE: CONTACT
# --------------------------------------------------------------------------
def contact():
    topics = "\n".join(
        f'              <option value="{k}" data-i18n="form_topic_{k}">form_topic_{k}</option>'
        for k in ["book", "vat", "ctax", "support", "other"])

    return head("meta_title_contact", "meta_desc_contact") + header("contact") + f'''
<main id="main">

  <section class="page-head section--navy">
    {MERIDIAN.format(extra="")}
    <div class="container">
      <div class="page-head-inner">
        <p class="eyebrow" data-i18n="contact_eyebrow">Contact</p>
        <h1 data-i18n="contact_h1">Let's talk about your business</h1>
        <p data-i18n="contact_intro">Visit us in Ajman, or work with us online from anywhere.</p>
      </div>
    </div>
    <div class="page-head-band">
      <img src="assets/img/skyline-band.jpg" alt="" width="1800" height="400" loading="lazy" decoding="async">
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="contact-grid">

        <!-- Column 1: office, online, direct contact -->
        <div>
          <div class="info-block">
            <h2 data-i18n="contact_office_h2">Ajman Office</h2>
            <address data-i18n="contact_address">Muwaihat 1, Al Tallah Road<br>Ajman, United Arab Emirates</address>
            <a class="map-link" href="{MAPS}" target="_blank" rel="noopener">
              <img src="assets/img/skyline-band.jpg" alt="" width="1800" height="400" loading="lazy" decoding="async">
              <span class="map-label"><span data-i18n="contact_directions">Get Directions</span>{ARROW}</span>
            </a>
          </div>

          <div class="info-block">
            <h2 data-i18n="contact_direct_h2">Direct Contact</h2>
            <ul class="contact-rows">
              <li><a class="contact-row" data-wa="consult" href="https://wa.me/971508821960" target="_blank" rel="noopener">
                <span class="ico" style="color:#25D366">{WA_ICON.replace('<svg ', '<svg width="18" height="18" ')}</span>
                <span><span class="k" data-i18n="label_whatsapp">WhatsApp</span><span class="v ltr">{PHONE_TEXT}</span></span>
              </a></li>
            </ul>
          </div>

          <div class="info-block">
            <h2 data-i18n="contact_online_h2">Online Consultation</h2>
            <p data-i18n="contact_online_p">Services can also be provided online from anywhere.</p>
          </div>
        </div>

        <!-- Column 2: message form -->
        <div class="form-card reveal">
          <h2 data-i18n="contact_form_h2">Send a Message</h2>
          <p class="lead" data-i18n="contact_form_intro">Tell us briefly what you need.</p>

          <form id="contactForm" novalidate>
            <div class="form-grid">
              <div class="form-row-2">
                <div class="field">
                  <label for="f-name"><span data-i18n="form_name">Name</span></label>
                  <input type="text" id="f-name" name="name" autocomplete="name"
                         data-i18n="form_name_ph" data-i18n-attr="placeholder">
                  <p class="field-error" data-i18n="form_err_name">Please enter your name.</p>
                </div>
                <div class="field">
                  <label for="f-email"><span data-i18n="form_email">Email</span></label>
                  <input type="email" id="f-email" name="email" autocomplete="email" dir="ltr"
                         data-i18n="form_email_ph" data-i18n-attr="placeholder">
                  <p class="field-error" data-i18n="form_err_email">Please enter a valid e-mail address.</p>
                </div>
              </div>

              <div class="form-row-2">
                <div class="field">
                  <label for="f-company">
                    <span data-i18n="form_company">Company</span>
                    <span class="opt">(<span data-i18n="form_company_optional">optional</span>)</span>
                  </label>
                  <input type="text" id="f-company" name="company" autocomplete="organization"
                         data-i18n="form_company_ph" data-i18n-attr="placeholder">
                </div>
                <div class="field">
                  <label for="f-topic"><span data-i18n="form_topic">How can we help?</span></label>
                  <select id="f-topic" name="topic">
                    <option value="" data-i18n="form_topic_choose">Please choose…</option>
{topics}
                  </select>
                </div>
              </div>

              <div class="field">
                <label for="f-message"><span data-i18n="form_message">Message</span></label>
                <textarea id="f-message" name="message" rows="5"
                          data-i18n="form_message_ph" data-i18n-attr="placeholder"></textarea>
                <p class="field-error" data-i18n="form_err_message">Please add a short message.</p>
              </div>

              <div class="form-actions">
                <button type="button" class="btn btn-primary" id="sendWhatsApp">
                  <span data-i18n="form_send_wa">Send on WhatsApp</span>{ARROW}
                </button>
              </div>
            </div>
          </form>

          <p class="form-status" id="formStatus" role="status" aria-live="polite"></p>
          <p class="form-note" data-i18n="form_note">This form prepares your message for WhatsApp.</p>
        </div>

      </div>
    </div>
  </section>

{cta_band()}
</main>

''' + footer()


# --------------------------------------------------------------------------
# PAGES: LEGAL (Impressum, Privacy)
#
# The legal text is written per-language by hand and is NOT part of i18n.js,
# so it lives in _source/legal/<name>.main.html and is wrapped here in the same
# header/footer as every other page. Edit the .main.html files, then rebuild.
# The <main> gets an explicit lang so screen readers use the right voice even
# when the visitor's interface language is different.
# --------------------------------------------------------------------------
def legal(name, title, desc, lang):
    with open(os.path.join("_source", "legal", f"{name}.main.html"), encoding="utf-8") as fh:
        main = fh.read().rstrip("\n")
    main = main.replace('<main id="main">', f'<main id="main" lang="{lang}">', 1)
    return (head(None, None, static_title=title, static_desc=desc, html_lang=lang)
            + header(None) + "\n" + main + "\n\n" + footer())


# --------------------------------------------------------------------------
if __name__ == "__main__":
    pages = {
        "index.html": home(),
        "about.html": about(),
        "services.html": services(),
        "pricing.html": pricing(),
        "contact.html": contact(),
        "impressum.html": legal("impressum", "Impressum | German Global Accounting LLC",
                                "Legal notice for German Global Accounting LLC.", "de"),
        "privacy.html": legal("privacy", "Privacy Policy | German Global Accounting LLC",
                              "Privacy information for German Global Accounting LLC.", "en"),
    }
    for name, html in pages.items():
        html = html.replace(" hidden-aria", "")
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"  {name:16s} {len(html) / 1024:5.1f} KB")
    print("Pages written.")
