#!/usr/bin/env python3
"""v15 image pipeline: new handshake hero, correctly cropped pricing photo,
and recompressed service-card images. Does not touch anything else."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
from PIL import Image, ImageEnhance, ImageFilter

OUT = "assets/img"

def grade(im, s=1.0):
    im = im.convert("RGB")
    im = ImageEnhance.Color(im).enhance(1 - 0.12 * s)
    im = ImageEnhance.Contrast(im).enhance(1 + 0.06 * s)
    return im

def save(im, name, q=78):
    p = os.path.join(OUT, name)
    im.save(p, "JPEG", quality=q, optimize=True, progressive=True)
    print(f"  {name:22s} {im.size[0]}x{im.size[1]} {os.path.getsize(p)/1024:5.0f} KB")

# --- Hero: the handshake photo (896x1342 source) -------------------------
src = Image.open("_source/photos/hero-handshake.png").convert("RGB")
save(grade(src, .8), "hero-lg.jpg", 80)                                   # desktop / tablet
sm = grade(src, .8).resize((640, round(640 * src.height / src.width)), Image.LANCZOS)
save(sm.filter(ImageFilter.UnsharpMask(1.0, 40, 3)), "hero-sm.jpg", 76)    # phones

# --- Pricing: full-frame crop of the original 3:2 photo -------------------
adv = Image.open("_source/photos/advisors-uae-flag.jpg").convert("RGB")     # 1536x1024
# 16:9 window that keeps the man's headdress, both faces, the calculator and the flag
crop = adv.crop((0, 40, 1536, 40 + 864))
big = grade(crop, .8).resize((1400, 788), Image.LANCZOS)
save(big.filter(ImageFilter.UnsharpMask(1.2, 55, 3)), "pricing-team.jpg", 78)
small = grade(crop, .8).resize((760, 428), Image.LANCZOS)
save(small.filter(ImageFilter.UnsharpMask(1.0, 45, 3)), "pricing-team-sm.jpg", 76)

# --- Recompress the rest (no re-crop) -------------------------------------
for n, size, q in [("svc-book.jpg", (1000, 833), 72), ("svc-vat.jpg", (1000, 833), 72),
                   ("svc-ctax.jpg", (1000, 833), 72), ("svc-support.jpg", (1000, 833), 72),
                   ("tower-tall.jpg", (800, 1000), 74), ("consult-lg.jpg", (1000, 750), 76),
                   ("consult-sm.jpg", (800, 700), 74), ("glass-band.jpg", (1400, 381), 72),
                   ("skyline-band.jpg", (1400, 311), 72)]:
    p = os.path.join(OUT, n)
    im = Image.open(p).convert("RGB")
    if im.size[0] > size[0]:
        im = im.resize(size, Image.LANCZOS)
    save(im, n, q)

# --- Delete images no page uses any more -----------------------------------
for n in ["hero-md.jpg", "hero2-lg.jpg", "hero2-md.jpg", "hero2-sm.jpg", "hero2-band.jpg", "hero-handshake.jpg"]:
    p = os.path.join(OUT, n)
    if os.path.exists(p):
        os.remove(p); print("  removed", n)
