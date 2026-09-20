#!/usr/bin/env python3
"""
Builds assets/styles.css from _source/src/styles.css.

  1. Every :hover rule is wrapped in @media (hover:hover) and (min-width:900px), so a tap
     on a phone can never leave a card "stuck" in its hover state.
  2. For the components listed in LIT_TARGETS a twin rule keyed to .scroll-lit is
     emitted for touch / narrow screens. site.js toggles .scroll-lit as the card
     crosses the middle of the viewport, so the "hover" animation plays on scroll.
  3. Comments and whitespace are stripped.

Edit _source/src/styles.css, then run:  python3 _source/build_css.py
"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "_source", "src", "styles.css")
OUT = os.path.join(ROOT, "assets", "styles.css")

HOVER_MQ = "(hover:hover) and (min-width:900px)"
TOUCH_MQ = "(hover:none),(max-width:899px)"
LIT_TARGETS = re.compile(
    r"^(\.card|\.why-item|\.process-step|\.addl-card|\.factor|\.place-card|\.chips li|"
    r"\.svc-detail|\.split-figure|\.pricing-feature|\.goal-card|\.quote-panel|"
    r"\.hero-v2-tags > span|\.contact-row|\.map-link)(?=[:.\s\[>]|$)")


def parse(css):
    """Split CSS into top-level nodes: ('c', comment) | ('r', prelude, body) | ('s', text)."""
    nodes, i, n = [], 0, len(css)
    while i < n:
        if css.startswith("/*", i):
            j = css.index("*/", i) + 2
            nodes.append(("c", css[i:j])); i = j; continue
        if css[i].isspace():
            i += 1; continue
        # read prelude up to '{' or ';'
        j, depth, q = i, 0, None
        while j < n:
            ch = css[j]
            if q:
                if ch == "\\": j += 1
                elif ch == q: q = None
            elif ch in "\"'": q = ch
            elif ch == "(": depth += 1
            elif ch == ")": depth -= 1
            elif css.startswith("/*", j):
                j = css.index("*/", j) + 1
            elif depth == 0 and ch in "{;": break
            j += 1
        prelude = css[i:j].strip()
        if j >= n or css[j] == ";":
            nodes.append(("s", prelude + ";")); i = j + 1; continue
        # block: find matching }
        d, k, q = 1, j + 1, None
        while k < n and d:
            ch = css[k]
            if q:
                if ch == "\\": k += 1
                elif ch == q: q = None
            elif ch in "\"'": q = ch
            elif css.startswith("/*", k): k = css.index("*/", k) + 1
            elif ch == "{": d += 1
            elif ch == "}": d -= 1
            k += 1
        nodes.append(("r", prelude, css[j + 1:k - 1])); i = k
    return nodes


def split_selectors(sel):
    parts, depth, cur, q = [], 0, "", None
    for ch in sel:
        if q:
            cur += ch
            if ch == q: q = None
            continue
        if ch in "\"'": q = ch
        if ch in "([": depth += 1
        if ch in ")]": depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur.strip()); cur = ""
        else:
            cur += ch
    if cur.strip(): parts.append(cur.strip())
    return parts


def emit(nodes, transform_hover=True, drop=None):
    out = []
    for nd in nodes:
        if nd[0] == "c":
            out.append(nd[1]); continue
        if nd[0] == "s":
            out.append(nd[1]); continue
        _, pre, body = nd
        if pre.startswith("@"):
            if re.match(r"@(media|supports)\b", pre):
                inner = emit(parse(body), transform_hover, drop)
                out.append(f"{pre}{{{inner}}}")
            else:
                out.append(f"{pre}{{{body}}}")
            continue
        sels = split_selectors(pre)
        if drop:
            sels = [s for s in sels if not drop(s)]
            if not sels: continue
        if not transform_hover:
            out.append(f"{', '.join(sels)}{{{body}}}"); continue
        hov = [s for s in sels if ":hover" in s]
        rest = [s for s in sels if ":hover" not in s]
        if rest: out.append(f"{', '.join(rest)}{{{body}}}")
        if hov:
            out.append(f"@media {HOVER_MQ}{{{', '.join(hov)}{{{body}}}}}")
            lit = [s.replace(":hover", ".scroll-lit") for s in hov]
            lit = [s for s in lit if LIT_TARGETS.match(s)]
            if lit:
                out.append(f"@media {TOUCH_MQ}{{{', '.join(lit)}{{{body}}}}}")
    return "\n".join(out)


def minify(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};])\s*", r"\1", css)
    css = re.sub(r":\s+", ":", css)
    css = re.sub(r",\s+", ",", css)
    css = css.replace(";}", "}")
    return css.strip()


def build():
    src = open(SRC, encoding="utf-8").read()
    css = emit(parse(src))
    out = minify(css)
    open(OUT, "w", encoding="utf-8").write(out)
    print(f"styles.css  {len(src)/1024:.0f} KB -> {len(out)/1024:.0f} KB")


if __name__ == "__main__":
    build()
