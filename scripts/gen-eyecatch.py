#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JA blog eyecatch generator (photoreal background + Japanese title) -> webp 2560x1440.
Runs in GitHub Actions (full internet). Free, no API key.
  python3 scripts/gen-eyecatch.py <slug> <title> <category> <out_webp_path>
Background: Pollinations (Flux). Fallback: category-colored gradient if generation fails.
Requires: Pillow, and a CJK font (fonts-noto-cjk).
"""
import sys, os, io, hashlib, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFont

slug, title, category, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
W, H = 2560, 1440

SCENES = {
  "請求書": "a clean modern Japanese office desk with an invoice document, calculator and a laptop, soft natural window light",
  "領収書": "a tidy desk with paper receipts, a red stamp and a fountain pen, warm soft lighting, finance",
  "見積書": "a bright business desk with a quotation document, pen and a cup of coffee, modern office",
  "履歴書": "a calm wooden desk with a Japanese resume sheet and a pen, soft daylight, job hunting",
  "職務経歴書": "a professional desk with career history documents and a laptop, bright modern office",
  "退職": "a quiet Japanese office desk with a white envelope and a pen beside a window, calm morning light",
  "税金・計算": "a desk with a calculator, tax documents and stacked coins, soft natural light",
  "転職・就活": "a bright desk with a resume and a laptop near a window, hopeful morning light",
  "税金": "a desk with a calculator, documents and coins, soft natural light",
}
base = SCENES.get(category, "a clean modern business desk with documents, a calculator and a laptop, soft natural light")
prompt = base + ", photorealistic, high detail, bright and airy, shallow depth of field, cinematic, no text, no words, no letters, no watermark"
seed = int(hashlib.md5(slug.encode("utf-8")).hexdigest(), 16) % 100000

def fetch_bg():
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
           + "?width=1280&height=720&seed=%d&nologo=true&model=flux" % seed)
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=150).read()
            im = Image.open(io.BytesIO(data)).convert("RGB")
            if im.width >= 512:
                return im.resize((W, H), Image.LANCZOS)
        except Exception as e:
            sys.stderr.write("pollinations attempt %d failed: %s\n" % (attempt, e))
    return None

def gradient_bg():
    COLORS = {"請求書": ((18,78,200),(52,150,235)), "領収書": ((16,120,96),(70,180,140)),
              "見積書": ((104,70,200),(165,120,240)), "履歴書": ((200,110,36),(240,170,84)),
              "職務経歴書": ((34,110,150),(84,170,205)), "退職": ((80,100,132),(140,160,188)),
              "税金・計算": ((190,62,82),(235,128,140)), "転職・就活": ((200,110,36),(240,170,84))}
    c1, c2 = COLORS.get(category, ((18,78,200),(52,150,235)))
    base_img = Image.new("RGB", (W, H), c1)
    top = Image.new("RGB", (W, H), c2)
    mask = Image.new("L", (W, H))
    md = ImageDraw.Draw(mask)
    for y in range(H):
        md.line([(0, y), (W, y)], fill=int(255 * y / H))
    return Image.composite(top, base_img, mask)

bg = fetch_bg() or gradient_bg()

# readability scrim: overall slight darken + strong bottom-left gradient
bg = Image.blend(bg, Image.new("RGB", (W, H), (8, 20, 38)), 0.26)
ov = Image.new("L", (W, H), 0)
od = ImageDraw.Draw(ov)
for y in range(H):
    a = int(210 * max(0.0, (y - H * 0.34)) / (H * 0.66))
    od.line([(0, y), (W, y)], fill=min(210, a))
bg = Image.composite(Image.new("RGB", (W, H), (6, 16, 32)), bg, ov)

draw = ImageDraw.Draw(bg)
FONTS = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
         "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Bold.otf",
         "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
         "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"]
def font(size):
    for p in FONTS:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except Exception: pass
    return ImageFont.load_default()

main = title.split("｜")[0].strip()

fsize = 158
f = font(fsize)
def wrap(text, fnt, maxw):
    lines, cur = [], ""
    for ch in text:
        if draw.textlength(cur + ch, font=fnt) <= maxw:
            cur += ch
        else:
            lines.append(cur); cur = ch
    if cur: lines.append(cur)
    return lines
lines = wrap(main, f, W - 360)
while len(lines) > 3 and fsize > 92:
    fsize -= 12; f = font(fsize); lines = wrap(main, f, W - 360)

# category pill
cf = font(58)
pill_w = draw.textlength(category, font=cf) + 64
py = H - 110 - (len(lines)) * (fsize + 20) - 120
draw.rounded_rectangle([150, py, 150 + pill_w, py + 94], radius=47, fill=(255, 212, 0))
draw.text((150 + 32, py + 14), category, font=cf, fill=(18, 28, 38))

# title
y = py + 130
x = 150
for ln in lines:
    draw.text((x + 5, y + 5), ln, font=f, fill=(0, 0, 0))
    draw.text((x, y), ln, font=f, fill=(255, 255, 255))
    y += fsize + 20

# brand
bf = font(46)
bt = "free-bizdocs.com"
draw.text((W - 150 - draw.textlength(bt, font=bf), H - 112), bt, font=bf, fill=(226, 238, 255))

os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
bg.save(out, "WEBP", quality=82, method=6)
print("generated", out, bg.size)
