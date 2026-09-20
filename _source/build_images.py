#!/usr/bin/env python3
"""
Asset pipeline for German Global Accounting.

Two jobs:
 1. Give every photograph the same colour grade so the set reads as one
    commissioned shoot rather than assorted stock.
 2. Produce art-directed crops (a real, separate crop per breakpoint) instead
    of letting one image be squeezed into every slot.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

SRC = "_source/photos"
OUT = "assets/img"
os.makedirs(OUT, exist_ok=True)

# Palette anchors (from the agreed colour system)
NAVY = (11, 31, 51)
DEEP_BLUE = (27, 58, 85)
WARM = (200, 169, 107)


def grade(im, strength=1.0):
    """Unifying grade: slight desaturation, contrast lift, cool shadows /
    warm highlights split-tone. Keeps skin tones believable."""
    im = im.convert("RGB")
    im = ImageEnhance.Color(im).enhance(1 - 0.16 * strength)
    im = ImageEnhance.Contrast(im).enhance(1 + 0.08 * strength)
    im = ImageEnhance.Brightness(im).enhance(1 + 0.02 * strength)

    px = im.load()
    w, h = im.size
    # Split-tone via lookup tables (fast, per-channel, luminance-weighted)
    lut_shadow = []
    for v in range(256):
        t = max(0.0, 1 - v / 140.0)          # shadow weight
        lut_shadow.append(t)
    r_l, g_l, b_l = [], [], []
    for v in range(256):
        t = lut_shadow[v] * 0.22 * strength
        u = max(0.0, (v - 150) / 105.0) * 0.10 * strength   # highlight weight
        r_l.append(int(max(0, min(255, v + (NAVY[0] - v) * t + (WARM[0] - v) * u))))
        g_l.append(int(max(0, min(255, v + (NAVY[1] - v) * t + (WARM[1] - v) * u))))
        b_l.append(int(max(0, min(255, v + (NAVY[2] - v) * t + (WARM[2] - v) * u))))
    im = im.point(r_l + g_l + b_l)
    return im


def duotone_navy(im, dark=(8, 20, 34), light=(150, 170, 190), mix=0.86):
    """Heavy navy duotone for dark hero / service-card photography, so text
    laid over the image is legible without a near-opaque colour panel."""
    g = ImageOps.grayscale(im)
    lut_r = [int(dark[0] + (light[0] - dark[0]) * (v / 255)) for v in range(256)]
    lut_g = [int(dark[1] + (light[1] - dark[1]) * (v / 255)) for v in range(256)]
    lut_b = [int(dark[2] + (light[2] - dark[2]) * (v / 255)) for v in range(256)]
    toned = Image.merge("RGB", (g.point(lut_r), g.point(lut_g), g.point(lut_b)))
    return Image.blend(im.convert("RGB"), toned, mix)


def emit(src, box, size, name, strength=1.0, sharpen=True, quality=84, source_dir=SRC, duotone=False):
    im = Image.open(os.path.join(source_dir, src))
    im = im.crop(box)
    im = grade(im, strength)
    if duotone:
        im = duotone_navy(im)
    im = im.resize(size, Image.LANCZOS)
    if sharpen:
        # Restore micro-contrast lost to resampling
        im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=72, threshold=3))
    path = os.path.join(OUT, name)
    im.save(path, "JPEG", quality=quality, optimize=True, progressive=True)
    kb = os.path.getsize(path) / 1024
    print(f"  {name:28s} {size[0]}x{size[1]:<6d} {kb:6.0f} KB")


print("Hero — client-supplied photo (advisors + UAE flag), three real crops per breakpoint:")
HERO_SRC = "advisors-uae-flag.jpg"   # 1536x1024, two advisors + UAE flag
emit(HERO_SRC, (0, 0, 1536, 1024), (1400, 1750), "hero2-lg.jpg")
emit(HERO_SRC, (60, 0, 1536, 1024), (1400, 1150), "hero2-md.jpg")
emit(HERO_SRC, (170, 0, 1370, 1024), (1000, 1100), "hero2-sm.jpg")
# Dark navy duotone of the same shot, for the small bottom feature-tag band
emit(HERO_SRC, (0, 40, 1536, 980), (1600, 500), "hero2-band.jpg", duotone=True, strength=0.6)

print("Service detail cards — dark navy duotone treatments:")
emit("why-panel.jpg", (0, 30, 616, 800), (1200, 1000), "svc-book.jpg", strength=1.1, duotone=True)
emit("contact-office.jpg", (0, 0, 1408, 950), (1200, 1000), "svc-vat.jpg", strength=1.1, duotone=True)
emit("pricing-team.jpg", (0, 0, 1000, 750), (1200, 1000), "svc-ctax.jpg", strength=1.1, duotone=True)
emit("about-office.jpg", (0, 0, 599, 448), (1200, 1000), "svc-support.jpg", strength=1.1, duotone=True)

print("Hero (art-directed per breakpoint):")
# Desktop: tall 4:5 column, both subjects in frame
emit("services-review.jpg", (250, 0, 1069, 1024), (1200, 1500), "hero-lg.jpg")
# Tablet: squarer
emit("services-review.jpg", (180, 0, 1330, 1024), (1200, 1069), "hero-md.jpg")
# Mobile: tighter, faces higher in frame so the scrim + headline sit over dead space
emit("services-review.jpg", (330, 60, 1210, 1040), (900, 1000), "hero-sm.jpg")

print("Feature photography:")
# About / consultation — calm, genuine, used at modest size (source is only 600px)
emit("about-office.jpg", (2, 0, 599, 448), (1100, 825), "consult-lg.jpg")
emit("about-office.jpg", (80, 20, 560, 440), (900, 788), "consult-sm.jpg")

print("Architectural texture (people cropped out deliberately):")
# Why-panel: skyline through glass, deep grade — sits inside a navy section
emit("why-panel.jpg", (0, 30, 616, 800), (1000, 1250), "tower-tall.jpg", strength=1.35)
# Wide skyline bands for page headers
emit("contact-office.jpg", (0, 18, 1408, 330), (1800, 400), "skyline-band.jpg", strength=1.2)
emit("pricing-team.jpg", (0, 28, 1000, 300), (1600, 435), "glass-band.jpg", strength=1.2)

print("Logo variants:")


def white_to_alpha(path, out, pad=0):
    """Unmultiply the logo from its white background so it can sit on the
    off-white header without a visible box. Preserves the silver tones."""
    im = Image.open(path).convert("RGB")
    im = ImageOps.crop(im, pad) if pad else im
    w, h = im.size
    out_im = Image.new("RGBA", (w, h))
    src = im.load()
    dst = out_im.load()
    for y in range(h):
        for x in range(w):
            r, g, b = src[x, y]
            m = min(r, g, b)
            a = 255 - m
            if a <= 2:
                dst[x, y] = (0, 0, 0, 0)
                continue
            af = a / 255.0
            # C = K*a + 255*(1-a)  ->  K = (C - 255*(1-a)) / a
            k = lambda c: max(0, min(255, int(round((c - 255 * (1 - af)) / af))))
            dst[x, y] = (k(r), k(g), k(b), a)
    out_im = out_im.crop(out_im.getbbox())
    out_im.save(out, "PNG", optimize=True)
    print(f"  {os.path.basename(out):28s} {out_im.size[0]}x{out_im.size[1]}")


white_to_alpha("_source/logo-nav.png", os.path.join(OUT, "logo-mark.png"))

# Footer / dark-background version keeps the original artwork on a light plate
Image.open("_source/logo-full.png").convert("RGB").save(
    os.path.join(OUT, "logo-plate.png"), "PNG", optimize=True)
print(f"  logo-plate.png")

# Favicon: crop the globe device out of the client's own artwork
lg = Image.open("_source/logo-full.png").convert("RGB")
globe = lg.crop((205, 8, 395, 190)).resize((180, 180), Image.LANCZOS)
fav = Image.new("RGB", (200, 200), "#0B1F33")
# Place the mark on navy by inverting the white field to navy
g = globe.load()
for y in range(180):
    for x in range(180):
        r, gg, b = g[x, y]
        if r > 245 and gg > 245 and b > 245:
            g[x, y] = NAVY
fav.paste(globe, (10, 10))
fav.save(os.path.join(OUT, "favicon.png"), "PNG", optimize=True)
print("  favicon.png                 200x200")
print("\nDone.")
