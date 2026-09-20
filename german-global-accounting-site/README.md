# German Global Accounting LLC — website

A static, trilingual (English / German / Arabic) site. No server, no build step
required to run it: upload the files as they are to any web host.

```
index.html  about.html  services.html  pricing.html  contact.html
impressum.html  privacy.html   (generated too — see _source/legal/)
assets/
  styles.css      BUILT file (minified) - do not edit by hand
  i18n.js         ALL site text, in three languages
  site.js         BUILT file - do not edit by hand
  fonts/          self-hosted Inter (latin + latin-ext)
  img/            processed photography and logo variants
_source/          build + QA scripts, original photos (not uploaded to the host)
```

## Changing the text

**All visible text lives in `assets/i18n.js`** — nothing user-facing is written
into the HTML. Each language is an object of the same keys:

```js
en: { nav_home: "Home",      hero_cta_primary: "Book a Consultation", … }
de: { nav_home: "Startseite", hero_cta_primary: "Beratungstermin vereinbaren", … }
ar: { nav_home: "الرئيسية",   hero_cta_primary: "احجز استشارة", … }
```

To change a sentence, edit it in all three objects. To add a new one, add the
key to all three, then reference it in the HTML as `data-i18n="your_key"`.

Two rules keep the three languages from drifting apart:

1. **Every language must have every key.** If one is missing, the site falls
   back to English and logs a warning in the browser console — it will never
   leave the previous language on screen, which is what used to cause German
   text to appear in the Arabic version.
2. **Attributes are translated too**, via `data-i18n-attr`:
   `data-i18n="form_name_ph" data-i18n-attr="placeholder"`.

Page titles and meta descriptions come from `data-title-key` / `data-desc-key`
on the `<html>` element of each page.

### Deliberately not translated

The registered company name, the e-mail address, the phone number, and the
terms *WhatsApp*, *VAT* and *IFRS* stay in Latin script in all three languages.
In the language picker each language is shown in its own language
(English / Deutsch / العربية) — that is the standard convention, not a mix.

## Language behaviour

The choice is stored in `localStorage` and persists across pages and visits.
An explicit `?lang=de` in the URL overrides it, so a link can be shared in a
specific language. First-time visitors get their browser language if it is one
of the three, otherwise English.

## The contact form

There is no backend. The form validates in the browser and then hands the
composed message and opens WhatsApp in a new tab.
Both work on plain static hosting. If you later add a server or a form service,
replace the two click handlers at the end of `assets/site.js`.

## `_source/` (for developers)

Not needed to run the site; keep it out of the public upload if you prefer.

| File | Purpose |
|---|---|
| `build_site.py` | Regenerates all seven HTML pages (the legal pages wrap `_source/legal/*.main.html`) from shared header/footer partials, so the navigation and footer cannot drift apart between pages. Run `python3 build_site.py` from the site root. |
| `build_images.py` | Re-crops and colour-grades the photography in `photos/` into `assets/img/`. |
| `qa.py` | Screenshots and checks all 5 pages × 3 languages × 2 breakpoints for overflow, untranslated text, cross-language leakage, colour contrast and broken images. |
| `qa_interact.py` | Tests the menu, language switching and persistence, and the contact form. |

**If you edit the HTML by hand, do not run `build_site.py` afterwards** — it
will overwrite your changes. Either edit `build_site.py` and regenerate, or
stop using it and edit the HTML directly. Both are fine; just pick one.

## Browser support

Modern evergreen browsers. Layout uses CSS logical properties throughout, which
is what makes the Arabic version a genuine right-to-left mirror rather than a
patched left-to-right page.

## Visual system ("Clinic Edition")

The look and motion are adapted from the AI Dental Luxury Clinic site: ink/gold/mint
palette, Fraunces + Inter, soft radii, pill buttons, glass header, clip-wipe reveals,
tilt/glare cards, sliding language pill. **All design tokens are in `assets/styles.css`
section 0**; motion is in sections 19-22; one `prefers-reduced-motion` block (section 25)
governs all of it. Fraunces and Readex Pro (Arabic) load from Google Fonts (see each
page's `<head>`); Inter is self-hosted.

To edit the legal pages, change `_source/legal/impressum.main.html` or `privacy.main.html`
and re-run `python3 _source/build_site.py`.


## v15 build workflow (styles and scripts)

`assets/styles.css` and `assets/site.js` are generated. Edit the readable sources instead:

| Edit | Then run |
|---|---|
| `_source/src/styles.css` | `python3 _source/build_css.py` |
| `_source/src/site.js` | `python3 _source/build_js.py` |
| `_source/build_site.py` (page markup) | `python3 _source/build_site.py` |
| photos in `_source/photos/` | `python3 _source/build_v15_images.py` |

`build_css.py` wraps every `:hover` rule so it only applies on real hover devices, and
generates a `.scroll-lit` twin so on phones the same animation plays as the card scrolls
past the middle of the screen. Do not run `build_images.py` any more (it targets the old hero).

Hosting: `.htaccess` enables compression and caching on Apache/LiteSpeed. On other hosts,
turn on gzip/Brotli and long cache lifetimes for `assets/`.
