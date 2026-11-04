#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate EN blog OG images (1200x630) matching the live style:
hyperreal photo bg + dark left scrim + category label + split two-line title
(white / accent) + left accent bar + bottom brand bar + corner triangle.
  python3 gen_en_og.py <out_dir>
Reads en_data.ARTICLES (slug, oglabel, ogline1, ogline2, c1, c2, subject, ogtag).
"""
import os, io, sys, time, random, hashlib, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

OUT = sys.argv[1] if len(sys.argv) > 1 else "out_og"
os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))
def _find_font():
    for p in [os.path.join(HERE, "NotoSansJP-VF.ttf"),
              os.path.join(HERE, "..", "NotoSansJP-VF.ttf"),
              os.path.join(HERE, "..", "..", "scripts", "NotoSansJP-VF.ttf")]:
        if os.path.exists(p):
            return p
    return os.path.join(HERE, "NotoSansJP-VF.ttf")
FONT = _find_font()
W, H = 1200, 630


def hx(s):
    s = str(s).lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def font(size, weight=800):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def fetch(subject, seed):
    prompt = (subject + ", hyperrealistic photograph, dark moody professional desk scene, "
              "shallow depth of field, cinematic soft lighting, muted tones, "
              "no text, no words, no letters, no watermark")
    for model, to in [("flux", 70), ("turbo", 45), ("flux", 70), ("turbo", 40)]:
        try:
            url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
                   + "?width=1200&height=630&seed=%d&nologo=true&model=%s" % (seed % 100000, model))
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=to).read()
            im = Image.open(io.BytesIO(data)).convert("RGB")
            if im.width < 400:
                raise ValueError("small")
            # crop a hair off the bottom (pollinations mark) then cover-fit
            im = im.crop((0, 0, im.width, int(im.height * 0.95)))
            return cover(im)
        except Exception as e:
            sys.stderr.write("poll(%s) fail: %s\n" % (model, e))
            time.sleep(2)
    return None


def cover(im):
    r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    x = (im.width - W) // 2
    y = (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


def fallback_bg(c1, c2, seed):
    rnd = random.Random(seed)
    base = Image.new("RGB", (W, H), (12, 18, 30))
    d = ImageDraw.Draw(base)
    for i in range(H):
        t = i / H
        d.line([(0, i), (W, i)], fill=(int(10 + 14 * t), int(16 + 22 * t), int(28 + 34 * t)))
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W * 0.5, -200, W * 1.25, 420], fill=tuple(int(x * 0.5) for x in c2))
    gd.ellipse([W * 0.55, 240, W * 1.3, 760], fill=tuple(int(x * 0.35) for x in c1))
    base = Image.blend(base, glow.filter(ImageFilter.GaussianBlur(170)), 0.5)
    return base


def grade(im):
    im = ImageEnhance.Brightness(im).enhance(0.82)
    im = ImageEnhance.Color(im).enhance(0.92)
    return im.convert("RGB")


def scrim(im, c1):
    # dark left-to-right gradient for text legibility + slight brand tint
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = ov.load()
    r0, g0, b0 = 8, 14, 24
    for x in range(W):
        t = x / W
        a = int(232 * (1 - t) ** 1.35 + 40)   # ~232 at left -> ~40 at right
        for y in range(H):
            px[x, y] = (r0, g0, b0, a)
    base = im.convert("RGBA")
    base.alpha_composite(ov)
    # subtle overall darken at very bottom for brand bar handled separately
    return base


def draw(slug, label, line1, line2, c1, c2, tagline, im):
    im = scrim(im, c1)
    d = ImageDraw.Draw(im)

    # left accent bar
    bx = 60
    d.rectangle([bx, 150, bx + 8, 470], fill=c2 + (255,))

    tx = 92
    # category label
    lf = font(23, 800)
    d.text((tx, 150), label.upper(), font=lf, fill=c2 + (255,))
    # tracking-ish: redraw spaced? keep simple (Noto has decent weight)

    # title
    tf = font(66, 800)
    y1 = 196
    d.text((tx, y1), line1, font=tf, fill=(255, 255, 255, 255))
    # measure line1 height
    bb = d.textbbox((tx, y1), line1, font=tf)
    y2 = bb[3] + 8
    d.text((tx, y2), line2, font=tf, fill=c2 + (255,))

    # bottom brand bar
    by = 556
    bar = Image.new("RGBA", (W, H - by), (9, 15, 26, 235))
    im.alpha_composite(bar, (0, by))
    d = ImageDraw.Draw(im)
    bf = font(26, 800)
    mf = font(21, 500)
    d.text((40, by + 22), "Free BizDoc", font=bf, fill=(255, 255, 255, 255))
    bw = d.textbbox((40, by + 22), "Free BizDoc", font=bf)[2]
    d.text((bw + 22, by + 26), "free-bizdocs.com  ·  " + tagline, font=mf, fill=(150, 170, 190, 255))

    # corner triangle bottom-right
    d.polygon([(W, by), (W, H), (W - (H - by), H)], fill=c2 + (255,))

    return im.convert("RGB")


def main():
    import en_data
    for a in en_data.ARTICLES:
        slug = a["slug"]
        seed = int(hashlib.md5(slug.encode()).hexdigest(), 16) % (2 ** 31)
        c1, c2 = hx(a.get("c1", "#0e7490")), hx(a.get("c2", "#2bb3c0"))
        im = fetch(a["subject"], seed)
        if im is None:
            im = fallback_bg(c1, c2, seed)
        else:
            im = grade(im)
        out = draw(slug, a["oglabel"], a["ogline1"], a["ogline2"], c1, c2,
                   a.get("ogtag", "free business docs, no sign-up"), im)
        out.save(os.path.join(OUT, slug + ".jpg"), "JPEG", quality=86, optimize=True)
        print("og:", slug)
    print("done EN og")


if __name__ == "__main__":
    main()
