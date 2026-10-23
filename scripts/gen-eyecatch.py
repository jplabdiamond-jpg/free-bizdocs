#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JA blog eyecatch generator -> webp 2560x1440.
Background: hyperrealistic AI photo (Pollinations) + cyber overlay (neon grid / glow / scanlines).
Fallback: procedural synthwave background when generation is unavailable.
Title: per-category font / size / color, overridable per article.
  python3 scripts/gen-eyecatch.py <slug> <title> <category> <out_webp_path> [style_json]
style_json (optional): {"font":"sans|serif","weight":int,"scale":float,
                        "colors":["#rrggbb","#rrggbb","#rrggbb"],"pill":"#rrggbb"}
Requires: Pillow. CJK fonts are bundled next to this script.
"""
import sys, os, io, json, time, math, random, hashlib, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

slug, title, category, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
STYLE = {}
if len(sys.argv) > 5 and sys.argv[5].strip():
    try: STYLE = json.loads(sys.argv[5])
    except Exception as e: sys.stderr.write("style parse error: %s\n" % e)

W, H = 2560, 1440
seed = int(hashlib.md5(slug.encode("utf-8")).hexdigest(), 16) % (2**31)
rnd = random.Random(seed)
HERE = os.path.dirname(os.path.abspath(__file__))

def hx(s):
    s = s.lstrip("#"); return (int(s[0:2],16), int(s[2:4],16), int(s[4:6],16))

# ---------- per-category style presets ----------
# font: sans(gothic) / serif(mincho); weight 100-900; scale multiplies base size;
# colors: 3 gradient stops for the title; accent: neon grid/glow tint; pill: pill color
PRESET = {
 "請求書":   {"font":"sans","weight":900,"scale":1.00,"colors":["#78f5ff","#ffffff","#ff78f0"],"accent":"#00e6ff","pill":"#ffdd00"},
 "領収書":   {"font":"sans","weight":900,"scale":1.00,"colors":["#00f0c0","#ffffff","#7af0ff"],"accent":"#00e6b4","pill":"#ffdd00"},
 "見積書":   {"font":"sans","weight":900,"scale":1.00,"colors":["#b98bff","#ffffff","#ff8ae0"],"accent":"#aa78ff","pill":"#ffdd00"},
 "履歴書":   {"font":"serif","weight":800,"scale":0.98,"colors":["#ffd27a","#ffffff","#ffe8a0"],"accent":"#ffb43c","pill":"#19e0ff"},
 "職務経歴書":{"font":"serif","weight":800,"scale":0.96,"colors":["#7ac8ff","#ffffff","#b0e0ff"],"accent":"#3cb4ff","pill":"#19e0ff"},
 "退職":     {"font":"serif","weight":800,"scale":0.98,"colors":["#b9c6f0","#ffffff","#8ad8ff"],"accent":"#96aadc","pill":"#19e0ff"},
 "税金・計算":{"font":"sans","weight":900,"scale":1.00,"colors":["#ff8a9c","#ffffff","#ffc87a"],"accent":"#ff5a78","pill":"#ffdd00"},
 "転職・就活":{"font":"sans","weight":900,"scale":1.00,"colors":["#ffc070","#ffffff","#ffe79a"],"accent":"#ff9646","pill":"#19e0ff"},
}
st = dict(PRESET.get(category, {"font":"sans","weight":900,"scale":1.00,
          "colors":["#78f5ff","#ffffff","#ff78f0"],"accent":"#00e6ff","pill":"#ffdd00"}))
st.update(STYLE)  # per-article overrides win
accent = hx(st["accent"]) if isinstance(st["accent"], str) else tuple(st["accent"])
cols = [hx(c) if isinstance(c, str) else tuple(c) for c in st["colors"]]
pill_col = hx(st["pill"]) if isinstance(st["pill"], str) else tuple(st["pill"])

# ---------- fonts ----------
FONT_FILES = {"sans": os.path.join(HERE, "NotoSansJP-VF.ttf"),
              "serif": os.path.join(HERE, "NotoSerifJP-VF.ttf")}
_SYS = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]
def font(size, weight=None, family=None):
    weight = st["weight"] if weight is None else weight
    family = st["font"] if family is None else family
    path = FONT_FILES.get(family, FONT_FILES["sans"])
    try:
        ft = ImageFont.truetype(path, size)
        try: ft.set_variation_by_axes([weight])
        except Exception: pass
        return ft
    except Exception:
        for p in _SYS:
            if os.path.exists(p):
                try: return ImageFont.truetype(p, size)
                except Exception: pass
    return ImageFont.load_default()

# ---------- background: hyperreal AI photo + cyber overlay ----------
SCENE = {
 "請求書":"a modern office desk with an invoice document, a laptop and a calculator by a window at dusk",
 "領収書":"a desk with paper receipts, a stamp and a pen, moody evening light",
 "見積書":"a business desk with a quotation document, a pen and a tablet",
 "履歴書":"a calm desk with a Japanese resume sheet and a pen near a window",
 "職務経歴書":"a professional desk with career documents and a laptop",
 "退職":"a quiet office desk with a white envelope and a pen by a window at night",
 "税金・計算":"a desk with a calculator, documents and coins",
 "転職・就活":"a bright desk with a resume and a laptop near a window",
}
scene = SCENE.get(category, "a modern business desk with documents, a calculator and a laptop")
prompt = (scene + ", hyperrealistic photograph, cinematic, subtle futuristic cyberpunk neon accents, "
          "holographic glow, neon rim lighting, dark high-tech ambiance, ultra detailed, 8k, "
          "no text, no words, no letters, no watermark")

def _get(model, to):
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
           + "?width=1280&height=720&seed=%d&nologo=true&model=%s" % (seed % 100000, model))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=to).read()
    im = Image.open(io.BytesIO(data)).convert("RGB")
    if im.width < 512: raise ValueError("too small")
    return im

def fetch_photo():
    for i, (model, to) in enumerate([("flux",80),("turbo",55),("flux",80),("turbo",55),("flux",80)]):
        try:
            im = _get(model, to)
            im = im.crop((0, 0, im.width, int(im.height * 0.93)))  # drop watermark strip
            return im.resize((W, H), Image.LANCZOS).convert("RGBA")
        except Exception as e:
            sys.stderr.write("pollinations %d (%s) failed: %s\n" % (i, model, e))
            time.sleep(3)
    return None

def cyber_overlay(img):
    """Add neon grid (bottom), edge glow and scanlines onto a photo (RGBA)."""
    # edge neon glow (screen)
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-500, 500, 700, 1700], fill=tuple(int(c*0.5) for c in accent))
    gd.ellipse([1900, -400, 3000, 700], fill=(90, 0, 110))
    glow = glow.filter(ImageFilter.GaussianBlur(200))
    img = ImageChops.screen(img.convert("RGB"), glow).convert("RGBA")
    # neon perspective grid in the lower area, semi-transparent
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gr = ImageDraw.Draw(grid)
    gc = accent + (110,)
    horizon = int(H * 0.68)
    yy, step = horizon + 8.0, 8.0
    while yy < H + 5:
        gr.line([(0, int(yy)), (W, int(yy))], fill=gc, width=3); step *= 1.18; yy += step
    vpx = W // 2
    for k in range(-20, 21):
        gr.line([(vpx, horizon), (vpx + k*180, H)], fill=gc, width=3)
    img = Image.alpha_composite(img, grid.filter(ImageFilter.GaussianBlur(7)))
    img = Image.alpha_composite(img, grid)
    hl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(hl).line([(0, horizon), (W, horizon)], fill=accent + (200,), width=5)
    img = Image.alpha_composite(img, hl.filter(ImageFilter.GaussianBlur(12)))
    # scanlines
    sl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sl)
    for y in range(0, H, 4):
        sd.line([(0, y), (W, y)], fill=(0, 0, 0, 36), width=1)
    img = Image.alpha_composite(img, sl)
    return img

def synthwave_bg():
    img = Image.new("RGB", (W, H), (6, 8, 24)); d = ImageDraw.Draw(img)
    top, bot = (16, 20, 58), (3, 4, 14)
    for y in range(H):
        t = y/H; d.line([(0,y),(W,y)], fill=tuple(int(top[i]+(bot[i]-top[i])*t) for i in range(3)))
    glow = Image.new("RGB", (W, H), (0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse([-360,-260,1000,1000], fill=(0,90,170)); gd.ellipse([1650,-160,2950,1050], fill=(130,0,140))
    gd.ellipse([760,820,2000,2050], fill=tuple(int(c*0.55) for c in accent))
    img = ImageChops.screen(img, glow.filter(ImageFilter.GaussianBlur(190)))
    grid = Image.new("RGBA", (W, H), (0,0,0,0)); gr = ImageDraw.Draw(grid); gc = accent + (170,)
    horizon = int(H*0.60); yy, step = horizon+10.0, 10.0
    while yy < H+5:
        gr.line([(0,int(yy)),(W,int(yy))], fill=gc, width=3); step*=1.17; yy+=step
    vpx = W//2
    for k in range(-22,23): gr.line([(vpx,horizon),(vpx+k*175,H)], fill=gc, width=3)
    img = Image.alpha_composite(img.convert("RGBA"), grid.filter(ImageFilter.GaussianBlur(9)))
    img = Image.alpha_composite(img, grid)
    hl = Image.new("RGBA", (W, H), (0,0,0,0)); ImageDraw.Draw(hl).line([(0,horizon),(W,horizon)], fill=(255,255,255,220), width=5)
    img = Image.alpha_composite(img, hl.filter(ImageFilter.GaussianBlur(14)))
    st2 = Image.new("RGBA", (W, H), (0,0,0,0)); sd = ImageDraw.Draw(st2)
    for _ in range(7):
        y = rnd.randint(40, horizon-120); x0 = rnd.randint(-200, W); ln = rnd.randint(360, 1000)
        col = (accent if rnd.random() < 0.6 else (255,60,220)) + (130,)
        sd.line([(x0,y),(x0+ln, y+rnd.randint(-30,30))], fill=col, width=rnd.choice([2,3,4]))
    img = Image.alpha_composite(img, st2.filter(ImageFilter.GaussianBlur(3)))
    return img

photo = fetch_photo()
bg = cyber_overlay(photo) if photo is not None else synthwave_bg()

# darken + bottom scrim for title legibility
bg = Image.blend(bg, Image.new("RGBA", (W, H), (3, 5, 18, 255)), 0.26)
ov = Image.new("L", (W, H), 0); od = ImageDraw.Draw(ov)
for y in range(H):
    a = int(230 * max(0.0, (y - H*0.28)) / (H*0.72)); od.line([(0,y),(W,y)], fill=min(230, a))
bg = Image.composite(Image.new("RGBA", (W, H), (3, 5, 18, 255)), bg, ov)
draw = ImageDraw.Draw(bg)

# ---------- title ----------
main = title.split("｜")[0].strip()
MAXW = W - 280
fsize = int(176 * float(st["scale"]))
f = font(fsize)
def wrap(text, fnt):
    lines, cur = [], ""
    for ch in text:
        if draw.textlength(cur+ch, font=fnt) <= MAXW: cur += ch
        else: lines.append(cur); cur = ch
    if cur: lines.append(cur)
    return lines
lines = wrap(main, f)
while len(lines) > 3 and fsize > 100:
    fsize -= 12; f = font(fsize); lines = wrap(main, f)
LH = fsize + 24
x = 150
title_bottom = H - 205
y0 = title_bottom - len(lines) * LH
pos = [(x, y0 + i*LH) for i in range(len(lines))]

# brand (bottom-right)
bf = font(48, weight=800, family="sans")
bt = "free-bizdocs.com"
bx = W - 150 - draw.textlength(bt, font=bf)
bglow = Image.new("RGBA", (W, H), (0,0,0,0))
ImageDraw.Draw(bglow).text((bx, H-122), bt, font=bf, fill=accent + (255,))
bg = Image.alpha_composite(bg, bglow.filter(ImageFilter.GaussianBlur(10)))
ImageDraw.Draw(bg).text((bx, H-122), bt, font=bf, fill=(235, 245, 255, 255))

# neon glow (two colors from palette ends)
g1, g2 = cols[0], cols[-1]
for color, rad, off in [(g1, 30, (0,0)), (g2, 34, (6,4))]:
    gl = Image.new("RGBA", (W, H), (0,0,0,0)); gld = ImageDraw.Draw(gl)
    for ln, (lx, ly) in zip(lines, pos):
        gld.text((lx+off[0], ly+off[1]), ln, font=f, fill=color + (255,))
    bg = Image.alpha_composite(bg, gl.filter(ImageFilter.GaussianBlur(rad)))
draw = ImageDraw.Draw(bg)
# dark outline base
for ln, (lx, ly) in zip(lines, pos):
    draw.text((lx, ly), ln, font=f, fill=(6,10,26), stroke_width=12, stroke_fill=(6,10,26))
# gradient-filled glyphs
maskimg = Image.new("L", (W, H), 0); md = ImageDraw.Draw(maskimg)
for ln, (lx, ly) in zip(lines, pos): md.text((lx, ly), ln, font=f, fill=255)
grad = Image.new("RGB", (W, H), cols[1]); gdd = ImageDraw.Draw(grad)
cA, cB, cC = cols[0], cols[1], cols[2]
for gx in range(0, W, 2):
    t = gx/W
    if t < 0.5:
        u = t/0.5; col = tuple(int(cA[i]+(cB[i]-cA[i])*u) for i in range(3))
    else:
        u = (t-0.5)/0.5; col = tuple(int(cB[i]+(cC[i]-cB[i])*u) for i in range(3))
    gdd.line([(gx,0),(gx,H)], fill=col, width=2)
bg.paste(grad, (0, 0), maskimg)

# category pill
draw = ImageDraw.Draw(bg)
cf = font(60, weight=800, family="sans")
pill_w = draw.textlength(category, font=cf) + 72
py = y0 - 128
pg = Image.new("RGBA", (W, H), (0,0,0,0))
ImageDraw.Draw(pg).rounded_rectangle([x, py, x+pill_w, py+100], radius=50, fill=pill_col + (255,))
bg = Image.alpha_composite(bg, pg.filter(ImageFilter.GaussianBlur(14)))
draw = ImageDraw.Draw(bg)
draw.rounded_rectangle([x, py, x+pill_w, py+100], radius=50, fill=pill_col + (255,))
draw.text((x+36, py+14), category, font=cf, fill=(16, 18, 30))

os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
bg.convert("RGB").save(out, "WEBP", quality=84, method=6)
print("generated", out, bg.size, "photo" if photo is not None else "synthwave")
