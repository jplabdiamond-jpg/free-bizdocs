#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JA blog eyecatch generator (photoreal background + Japanese title) -> webp 2560x1440.
Runs in GitHub Actions (full internet). Free, no API key.
  python3 scripts/gen-eyecatch.py <slug> <title> <category> <out_webp_path>
Background: Pollinations (Flux/Turbo). Fallback: category-colored gradient if generation fails.
Requires: Pillow, and a CJK font (fonts-noto-cjk).
"""
import sys, os, io, time, hashlib, urllib.parse, urllib.request
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
}
base = SCENES.get(category, "a clean modern business desk with documents, a calculator and a laptop, soft natural light")
prompt = base + ", photorealistic, high detail, bright and airy, shallow depth of field, cinematic, no text, no words, no letters, no watermark"
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
    # 5 attempts; flux first (quality), turbo later (faster/more reliable)
    plan = [("flux", 85), ("flux", 85), ("turbo", 60), ("turbo", 60), ("flux", 85)]
    for i, (model, to) in enumerate(plan):
        try:
            im = _get(model, to)
            # crop bottom strip to drop the pollinations watermark, then upscale
            im = im.crop((0, 0, im.width, int(im.height * 0.93)))
            return im.resize((W, H), Image.LANCZOS)
        except Exception as e:
            sys.stderr.write("pollinations attempt %d (%s) failed: %s\n" % (i, model, e))
            time.sleep(3)
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

# readability scrim: slight overall darken + strong bottom gradient
bg = Image.blend(bg, Image.new("RGB", (W, H), (8, 20, 38)), 0.24)
ov = Image.new("L", (W, H), 0)
od = ImageDraw.Draw(ov)
for y in range(H):
    a = int(215 * max(0.0, (y - H * 0.30)) / (H * 0.70))
    od.line([(0, y), (W, y)], fill=min(215, a))
bg = Image.composite(Image.new("RGB", (W, H), (6, 16, 32)), bg, ov)

draw = ImageDraw.Draw(bg)
FONTS = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
         "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Bold.otf",
         "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"]
def font(size):
    for p in FONTS:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except Exception: pass
    return ImageFont.load_default()

main = title.split("｜")[0].strip()
MAXW = W - 300
fsize = 160
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
while len(lines) > 3 and fsize > 96:
    fsize -= 12; f = font(fsize); lines = wrap(main, f)

LH = fsize + 22
x = 150
bf = font(46)
bt = "free-bizdocs.com"
draw.text((W - 150 - draw.textlength(bt, font=bf), H - 120), bt, font=bf, fill=(228, 240, 255))

title_bottom = H - 210
y = title_bottom - len(lines) * LH
cf = font(58)
pill_w = draw.textlength(category, font=cf) + 64
py = y - 118
draw.rounded_rectangle([x, py, x + pill_w, py + 94], radius=47, fill=(255, 212, 0))
draw.text((x + 32, py + 14), category, font=cf, fill=(18, 28, 38))
for ln in lines:
    draw.text((x + 5, y + 5), ln, font=f, fill=(0, 0, 0))
    draw.text((x, y), ln, font=f, fill=(255, 255, 255))
    y += LH

os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
bg.save(out, "WEBP", quality=82, method=6)
print("generated", out, bg.size)
