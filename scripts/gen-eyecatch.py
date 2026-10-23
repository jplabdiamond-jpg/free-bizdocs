#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JA blog eyecatch generator -> webp 2560x1440.
Cyberpunk / futuristic neon background + flashy neon-gradient Japanese title.
Runs in GitHub Actions (full internet). Free, no API key.
  python3 scripts/gen-eyecatch.py <slug> <title> <category> <out_webp_path>
Background: Pollinations (Flux/Turbo). Fallback: neon gradient if generation fails.
Requires: Pillow, and a CJK font (fonts-noto-cjk).
"""
import sys, os, io, time, hashlib, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

slug, title, category, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
W, H = 2560, 1440

OBJ = {
  "請求書": "a glowing holographic invoice document floating in the air",
  "領収書": "a glowing holographic receipt and a neon stamp",
  "見積書": "a glowing holographic quotation panel",
  "履歴書": "a futuristic holographic resume profile card",
  "職務経歴書": "glowing holographic career data panels",
  "退職": "a glowing digital envelope hologram",
  "税金・計算": "glowing holographic numbers and a neon calculator",
  "転職・就活": "a futuristic holographic profile and rising neon graph",
}
obj = OBJ.get(category, "a glowing holographic business document")
prompt = (obj + ", futuristic cyberpunk scene, glowing neon holographic interface, dark high-tech "
          "background, vivid neon cyan magenta and electric blue, dramatic volumetric lighting, "
          "particles and light trails, sci-fi 3D render, ultra detailed, no text, no words, no letters, no watermark")
seed = int(hashlib.md5(slug.encode("utf-8")).hexdigest(), 16) % 100000

def _get(model, to):
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
           + "?width=1280&height=720&seed=%d&nologo=true&model=%s" % (seed, model))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=to).read()
    im = Image.open(io.BytesIO(data)).convert("RGB")
    if im.width < 512:
        raise ValueError("too small")
    return im

def fetch_bg():
    plan = [("flux", 85), ("flux", 85), ("turbo", 60), ("turbo", 60), ("flux", 85)]
    for i, (model, to) in enumerate(plan):
        try:
            im = _get(model, to)
            im = im.crop((0, 0, im.width, int(im.height * 0.93)))  # drop watermark strip
            return im.resize((W, H), Image.LANCZOS)
        except Exception as e:
            sys.stderr.write("pollinations attempt %d (%s) failed: %s\n" % (i, model, e))
            time.sleep(3)
    return None

def neon_gradient_bg():
    # fallback: dark base + diagonal cyan->magenta neon glow blobs
    base = Image.new("RGB", (W, H), (8, 10, 26))
    glow = Image.new("RGB", (W, H), (8, 10, 26))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-400, 200, 1200, 1600], fill=(20, 80, 150))
    gd.ellipse([1500, -300, 2900, 1100], fill=(120, 20, 120))
    glow = glow.filter(ImageFilter.GaussianBlur(220))
    return Image.blend(base, glow, 0.9)

bg = (fetch_bg() or neon_gradient_bg()).convert("RGBA")

# darken + bottom scrim for title legibility
bg = Image.blend(bg, Image.new("RGBA", (W, H), (4, 6, 20, 255)), 0.30)
ov = Image.new("L", (W, H), 0)
od = ImageDraw.Draw(ov)
for y in range(H):
    a = int(225 * max(0.0, (y - H * 0.28)) / (H * 0.72))
    od.line([(0, y), (W, y)], fill=min(225, a))
bg = Image.composite(Image.new("RGBA", (W, H), (3, 5, 18, 255)), bg, ov)

draw = ImageDraw.Draw(bg)
FONTS = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc",
         "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
         "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Bold.otf",
         "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"]
def font(size):
    for p in FONTS:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except Exception: pass
    return ImageFont.load_default()

main = title.split("｜")[0].strip()
MAXW = W - 280
fsize = 172
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
while len(lines) > 3 and fsize > 100:
    fsize -= 12; f = font(fsize); lines = wrap(main, f)

LH = fsize + 24
x = 150
title_bottom = H - 205
y0 = title_bottom - len(lines) * LH
pos = [(x, y0 + i * LH) for i in range(len(lines))]

# brand (bottom-right) with soft cyan glow
bf = font(48)
bt = "free-bizdocs.com"
bx = W - 150 - draw.textlength(bt, font=bf)
bglow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(bglow).text((bx, H - 122), bt, font=bf, fill=(0, 225, 255, 255))
bg = Image.alpha_composite(bg, bglow.filter(ImageFilter.GaussianBlur(10)))
ImageDraw.Draw(bg).text((bx, H - 122), bt, font=bf, fill=(235, 245, 255, 255))

# ---- flashy neon title ----
# 1) outer neon glow (cyan + magenta)
for color, rad, off in [((0, 229, 255), 30, (0, 0)), ((255, 46, 224), 34, (6, 4))]:
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gld = ImageDraw.Draw(gl)
    for ln, (lx, ly) in zip(lines, pos):
        gld.text((lx + off[0], ly + off[1]), ln, font=f, fill=color + (255,))
    bg = Image.alpha_composite(bg, gl.filter(ImageFilter.GaussianBlur(rad)))
bg = Image.alpha_composite(bg, Image.new("RGBA", (W, H), (0, 0, 0, 0)))  # noop keep RGBA
draw = ImageDraw.Draw(bg)

# 2) dark outline base for legibility
for ln, (lx, ly) in zip(lines, pos):
    draw.text((lx, ly), ln, font=f, fill=(6, 10, 26), stroke_width=12, stroke_fill=(6, 10, 26))

# 3) gradient-filled glyphs (cyan -> white -> magenta)
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

# ---- category pill (neon yellow) ----
draw = ImageDraw.Draw(bg)
cf = font(60)
pill_w = draw.textlength(category, font=cf) + 72
py = y0 - 128
pill_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(pill_glow).rounded_rectangle([x, py, x + pill_w, py + 100], radius=50, fill=(255, 221, 0, 255))
bg = Image.alpha_composite(bg, pill_glow.filter(ImageFilter.GaussianBlur(14)))
draw = ImageDraw.Draw(bg)
draw.rounded_rectangle([x, py, x + pill_w, py + 100], radius=50, fill=(255, 221, 0, 255))
draw.text((x + 36, py + 14), category, font=cf, fill=(16, 18, 30))

os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
bg.convert("RGB").save(out, "WEBP", quality=82, method=6)
print("generated", out, bg.size)
