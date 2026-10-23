#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JA blog eyecatch generator -> webp 2560x1440.
Flashy cyberpunk / synthwave background (procedural, reliable) + neon-gradient glowing title.
  python3 scripts/gen-eyecatch.py <slug> <title> <category> <out_webp_path>
Requires: Pillow, and a CJK font (fonts-noto-cjk). No network needed.
"""
import sys, os, math, random, hashlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

slug, title, category, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
W, H = 2560, 1440
seed = int(hashlib.md5(slug.encode("utf-8")).hexdigest(), 16) % (2**31)
rnd = random.Random(seed)

# per-category accent (secondary neon tint) — keeps variety between genres
ACCENT = {
  "請求書": (0, 230, 255), "領収書": (0, 235, 180), "見積書": (170, 120, 255),
  "履歴書": (255, 170, 60), "職務経歴書": (60, 180, 255), "退職": (150, 170, 220),
  "税金・計算": (255, 90, 120), "転職・就活": (255, 150, 70),
}
acc = ACCENT.get(category, (0, 230, 255))

def cyber_bg():
    # deep vertical gradient
    img = Image.new("RGB", (W, H), (6, 8, 24))
    d = ImageDraw.Draw(img)
    top, bot = (16, 20, 58), (3, 4, 14)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    # big soft neon glow orbs (screen-blended)
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-360, -260, 1000, 1000], fill=(0, 90, 170))
    gd.ellipse([1650, -160, 2950, 1050], fill=(130, 0, 140))
    gd.ellipse([760, 820, 2000, 2050], fill=tuple(int(c * 0.55) for c in acc))
    glow = glow.filter(ImageFilter.GaussianBlur(190))
    img = ImageChops.screen(img, glow)
    # synthwave perspective grid (bottom)
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gr = ImageDraw.Draw(grid)
    gcol = acc + (170,)
    horizon = int(H * 0.60)
    yy, step = horizon + 10.0, 10.0
    while yy < H + 5:
        gr.line([(0, int(yy)), (W, int(yy))], fill=gcol, width=3)
        step *= 1.17; yy += step
    vpx = W // 2
    for k in range(-22, 23):
        bx = vpx + k * 175
        gr.line([(vpx, horizon), (bx, H)], fill=gcol, width=3)
    glow_grid = grid.filter(ImageFilter.GaussianBlur(9))
    img = Image.alpha_composite(img.convert("RGBA"), glow_grid)
    img = Image.alpha_composite(img, grid)
    # horizon glow line
    hl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(hl).line([(0, horizon), (W, horizon)], fill=(255, 255, 255, 220), width=5)
    img = Image.alpha_composite(img, hl.filter(ImageFilter.GaussianBlur(14)))
    img = Image.alpha_composite(img, hl.filter(ImageFilter.GaussianBlur(2)))
    # light streaks (upper area)
    st = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    for _ in range(7):
        y = rnd.randint(40, horizon - 120); x0 = rnd.randint(-200, W); ln = rnd.randint(360, 1000)
        col = (acc if rnd.random() < 0.6 else (255, 60, 220)) + (130,)
        sd.line([(x0, y), (x0 + ln, y + rnd.randint(-30, 30))], fill=col, width=rnd.choice([2, 3, 4]))
    img = Image.alpha_composite(img, st.filter(ImageFilter.GaussianBlur(3)))
    # faint particles
    pt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pt)
    for _ in range(90):
        x = rnd.randint(0, W); y = rnd.randint(0, int(H * 0.7)); r = rnd.choice([2, 2, 3, 4])
        pd.ellipse([x, y, x + r, y + r], fill=(220, 240, 255, rnd.randint(60, 160)))
    img = Image.alpha_composite(img, pt.filter(ImageFilter.GaussianBlur(1)))
    return img.convert("RGBA")

bg = cyber_bg()

# darken + bottom scrim for title legibility
bg = Image.blend(bg, Image.new("RGBA", (W, H), (3, 5, 18, 255)), 0.22)
ov = Image.new("L", (W, H), 0)
od = ImageDraw.Draw(ov)
for y in range(H):
    a = int(225 * max(0.0, (y - H * 0.30)) / (H * 0.70))
    od.line([(0, y), (W, y)], fill=min(225, a))
bg = Image.composite(Image.new("RGBA", (W, H), (3, 5, 18, 255)), bg, ov)

draw = ImageDraw.Draw(bg)
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "NotoSansJP-VF.ttf")
_SYS = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"]
def font(size, weight=900):
    try:
        ft = ImageFont.truetype(FONT_PATH, size)
        try: ft.set_variation_by_axes([weight])
        except Exception: pass
        return ft
    except Exception:
        for p in _SYS:
            if os.path.exists(p):
                try: return ImageFont.truetype(p, size)
                except Exception: pass
    return ImageFont.load_default()

main = title.split("｜")[0].strip()
MAXW = W - 280
fsize = 176
f = font(fsize)
def wrap(text, fnt):
    lines, cur = [], ""
    for ch in text:
        if draw.textlength(cur + ch, font=fnt) <= MAXW:
            cur += ch
        else:
            lines.append(cur); cur = ch
    if cur: lines.append(cur)
    return lines
lines = wrap(main, f)
while len(lines) > 3 and fsize > 104:
    fsize -= 12; f = font(fsize); lines = wrap(main, f)

LH = fsize + 24
x = 150
title_bottom = H - 205
y0 = title_bottom - len(lines) * LH
pos = [(x, y0 + i * LH) for i in range(len(lines))]

# brand (bottom-right) with cyan glow
bf = font(48, 800)
bt = "free-bizdocs.com"
bx = W - 150 - draw.textlength(bt, font=bf)
bglow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(bglow).text((bx, H - 122), bt, font=bf, fill=(0, 225, 255, 255))
bg = Image.alpha_composite(bg, bglow.filter(ImageFilter.GaussianBlur(10)))
ImageDraw.Draw(bg).text((bx, H - 122), bt, font=bf, fill=(235, 245, 255, 255))

# ---- flashy neon title ----
for color, rad, off in [((0, 229, 255), 30, (0, 0)), ((255, 46, 224), 34, (6, 4))]:
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gld = ImageDraw.Draw(gl)
    for ln, (lx, ly) in zip(lines, pos):
        gld.text((lx + off[0], ly + off[1]), ln, font=f, fill=color + (255,))
    bg = Image.alpha_composite(bg, gl.filter(ImageFilter.GaussianBlur(rad)))
draw = ImageDraw.Draw(bg)
for ln, (lx, ly) in zip(lines, pos):
    draw.text((lx, ly), ln, font=f, fill=(6, 10, 26), stroke_width=12, stroke_fill=(6, 10, 26))
maskimg = Image.new("L", (W, H), 0)
md = ImageDraw.Draw(maskimg)
for ln, (lx, ly) in zip(lines, pos):
    md.text((lx, ly), ln, font=f, fill=255)
grad = Image.new("RGB", (W, H), (255, 255, 255))
gdd = ImageDraw.Draw(grad)
cA, cB, cC = (120, 245, 255), (255, 255, 255), (255, 120, 240)
for gx in range(0, W, 2):
    t = gx / W
    if t < 0.5:
        u = t / 0.5; col = tuple(int(cA[i] + (cB[i] - cA[i]) * u) for i in range(3))
    else:
        u = (t - 0.5) / 0.5; col = tuple(int(cB[i] + (cC[i] - cB[i]) * u) for i in range(3))
    gdd.line([(gx, 0), (gx, H)], fill=col, width=2)
bg.paste(grad, (0, 0), maskimg)

# ---- category pill (neon yellow with glow) ----
draw = ImageDraw.Draw(bg)
cf = font(60, 800)
pill_w = draw.textlength(category, font=cf) + 72
py = y0 - 128
pill_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(pill_glow).rounded_rectangle([x, py, x + pill_w, py + 100], radius=50, fill=(255, 221, 0, 255))
bg = Image.alpha_composite(bg, pill_glow.filter(ImageFilter.GaussianBlur(14)))
draw = ImageDraw.Draw(bg)
draw.rounded_rectangle([x, py, x + pill_w, py + 100], radius=50, fill=(255, 221, 0, 255))
draw.text((x + 36, py + 14), category, font=cf, fill=(16, 18, 30))

os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
bg.convert("RGB").save(out, "WEBP", quality=84, method=6)
print("generated", out, bg.size)
