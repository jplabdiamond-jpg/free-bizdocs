#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JA blog eyecatch generator -> webp 2560x1440 (note-style, flashy).
Background: hyperrealistic AI photo (Pollinations) with cinematic neon grade.
            Falls back to a procedural synthwave scene when generation is unavailable.
Title: bold white with thick black outline + accent glow, per-word color emphasis,
       per-category/per-article font / size / color, optional English subtitle.
  python3 scripts/gen-eyecatch.py <slug> <title> <category> <out_webp> [style_json]
style_json keys (all optional):
  font:"sans|serif", weight:int, scale:float, pill:"#hex",
  emph:"強調する語", emphcolor:"#hex", en:"English subtitle",
  colors:["#a","#b","#c"]  (if set -> neon gradient title instead of white)
Fonts are bundled next to this script.
"""
import sys, os, io, json, time, random, hashlib, urllib.parse, urllib.request
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
    s = str(s).lstrip("#"); return (int(s[0:2],16), int(s[2:4],16), int(s[4:6],16))

PRESET = {
 "請求書":   {"font":"sans","weight":900,"scale":1.00,"accent":"#00e6ff","pill":"#ffdd00","emphcolor":"#ffd400"},
 "領収書":   {"font":"sans","weight":900,"scale":1.00,"accent":"#00e6b4","pill":"#ffdd00","emphcolor":"#00f0c0"},
 "見積書":   {"font":"sans","weight":900,"scale":1.00,"accent":"#aa78ff","pill":"#ffdd00","emphcolor":"#c9a3ff"},
 "履歴書":   {"font":"serif","weight":900,"scale":0.98,"accent":"#ffb43c","pill":"#19e0ff","emphcolor":"#ffcf5a"},
 "職務経歴書":{"font":"serif","weight":900,"scale":0.96,"accent":"#3cb4ff","pill":"#19e0ff","emphcolor":"#7ac8ff"},
 "退職":     {"font":"serif","weight":900,"scale":0.98,"accent":"#96aadc","pill":"#19e0ff","emphcolor":"#ff5a78"},
 "税金・計算":{"font":"sans","weight":900,"scale":1.00,"accent":"#ff5a78","pill":"#ffdd00","emphcolor":"#ff5a78"},
 "転職・就活":{"font":"sans","weight":900,"scale":1.00,"accent":"#ff9646","pill":"#19e0ff","emphcolor":"#ffd400"},
}
st = dict(PRESET.get(category, {"font":"sans","weight":900,"scale":1.00,"accent":"#00e6ff","pill":"#ffdd00","emphcolor":"#ffd400"}))
st.update(STYLE)
accent = hx(st["accent"]) if isinstance(st["accent"], str) else tuple(st["accent"])
pill_col = hx(st["pill"]) if isinstance(st["pill"], str) else tuple(st["pill"])
emph_text = st.get("emph", "")
emph_color = hx(st.get("emphcolor", "#ffd400"))
en_sub = st.get("en", "")
grad_cols = [hx(c) if isinstance(c, str) else tuple(c) for c in st["colors"]] if st.get("colors") else None

FONT_FILES = {"sans": os.path.join(HERE,"NotoSansJP-VF.ttf"), "serif": os.path.join(HERE,"NotoSerifJP-VF.ttf")}
_SYS = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]
def font(size, weight=None, family=None):
    weight = st["weight"] if weight is None else weight
    family = st["font"] if family is None else family
    try:
        ft = ImageFont.truetype(FONT_FILES.get(family, FONT_FILES["sans"]), size)
        try: ft.set_variation_by_axes([weight])
        except Exception: pass
        return ft
    except Exception:
        for p in _SYS:
            if os.path.exists(p):
                try: return ImageFont.truetype(p, size)
                except Exception: pass
    return ImageFont.load_default()

# ---------- background ----------
SCENE = {
 "請求書":"a sleek modern office desk with an invoice document, a laptop and a calculator, neon-lit night city through the window",
 "領収書":"a desk with paper receipts and a stamp under dramatic neon lighting, cinematic",
 "見積書":"a business desk with a quotation document and a tablet, neon reflections, cinematic",
 "履歴書":"a calm desk with a Japanese resume and a pen near a window, cinematic rim light",
 "職務経歴書":"a professional desk with career documents and a laptop, cinematic neon ambiance",
 "退職":"a quiet office desk with a white envelope by a window at night, moody neon light",
 "税金・計算":"a desk with a calculator, documents and stacked coins, dramatic cinematic lighting",
 "転職・就活":"a bright desk with a resume and laptop near a window, cinematic hopeful light",
}
scene = SCENE.get(category, "a sleek modern business desk with documents and a laptop, cinematic neon lighting")
prompt = (scene + ", hyperrealistic photograph, ultra detailed, 8k, cinematic color grading, "
          "dramatic lighting, shallow depth of field, futuristic high-tech atmosphere, "
          "no text, no words, no letters, no watermark")

def _get(model, to):
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
           + "?width=1280&height=720&seed=%d&nologo=true&model=%s" % (seed % 100000, model))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=to).read()
    im = Image.open(io.BytesIO(data)).convert("RGB")
    if im.width < 512: raise ValueError("small")
    return im

def fetch_photo():
    for i,(m,to) in enumerate([("flux",80),("turbo",55),("flux",80),("turbo",55),("flux",80),("turbo",50)]):
        try:
            im = _get(m, to); im = im.crop((0,0,im.width,int(im.height*0.93)))
            return im.resize((W,H), Image.LANCZOS).convert("RGB")
        except Exception as e:
            sys.stderr.write("poll %d(%s) fail: %s\n" % (i,m,e)); time.sleep(3)
    return None

def grade_photo(im):
    # cinematic neon grade: edge glow + vignette (keeps it hyperreal, light touch)
    glow = Image.new("RGB",(W,H),(0,0,0)); gd = ImageDraw.Draw(glow)
    gd.ellipse([-500,500,700,1700], fill=tuple(int(c*0.45) for c in accent))
    gd.ellipse([1900,-400,3000,700], fill=(80,0,100))
    im = ImageChops.screen(im, glow.filter(ImageFilter.GaussianBlur(210)))
    vig = Image.new("L",(W,H),0); ImageDraw.Draw(vig).ellipse([-W*0.25,-H*0.25,W*1.25,H*1.25], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(300))
    im = Image.composite(im, ImageChops.multiply(im, Image.new("RGB",(W,H),(120,120,140))), vig)
    return im.convert("RGBA")

def synthwave_bg():
    img = Image.new("RGB",(W,H),(6,8,24)); d = ImageDraw.Draw(img)
    top,bot=(16,20,58),(3,4,14)
    for y in range(H):
        t=y/H; d.line([(0,y),(W,y)], fill=tuple(int(top[i]+(bot[i]-top[i])*t) for i in range(3)))
    glow = Image.new("RGB",(W,H),(0,0,0)); gd = ImageDraw.Draw(glow)
    gd.ellipse([-360,-260,1000,1000], fill=(0,90,170)); gd.ellipse([1650,-160,2950,1050], fill=(130,0,140))
    gd.ellipse([760,820,2000,2050], fill=tuple(int(c*0.55) for c in accent))
    img = ImageChops.screen(img, glow.filter(ImageFilter.GaussianBlur(190)))
    grid = Image.new("RGBA",(W,H),(0,0,0,0)); gr = ImageDraw.Draw(grid); gc = accent+(170,)
    horizon=int(H*0.60); yy,step=horizon+10.0,10.0
    while yy<H+5:
        gr.line([(0,int(yy)),(W,int(yy))], fill=gc, width=3); step*=1.17; yy+=step
    for k in range(-22,23): gr.line([(W//2,horizon),(W//2+k*175,H)], fill=gc, width=3)
    img = Image.alpha_composite(img.convert("RGBA"), grid.filter(ImageFilter.GaussianBlur(9)))
    img = Image.alpha_composite(img, grid)
    hl = Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(hl).line([(0,horizon),(W,horizon)], fill=(255,255,255,220), width=5)
    return Image.alpha_composite(img, hl.filter(ImageFilter.GaussianBlur(14)))

photo = fetch_photo()
bg = grade_photo(photo) if photo is not None else synthwave_bg()

# contrast scrim: darken left side + top + bottom so the title pops (note-style)
scr = Image.new("L",(W,H),0); sd = ImageDraw.Draw(scr)
for x in range(W):
    a = int(210 * max(0.0, 1.0 - x/(W*0.72)))
    sd.line([(x,0),(x,H)], fill=a)
bg = Image.composite(Image.new("RGBA",(W,H),(3,5,16,255)), bg, scr)
tb = Image.new("L",(W,H),0); td = ImageDraw.Draw(tb)
for y in range(H):
    a = 150 if y < H*0.30 else (int(180*max(0.0,(y-H*0.70))/(H*0.30)) if y>H*0.70 else 0)
    td.line([(0,y),(W,y)], fill=min(200,a))
bg = Image.composite(Image.new("RGBA",(W,H),(3,5,16,255)), bg, tb)
draw = ImageDraw.Draw(bg)

# ---------- title (segment colors, heavy outline, glow) ----------
main = title.split("｜")[0].strip()
base_col = (255,255,255)
# build per-char color list with keyword emphasis
chars = []
if emph_text and emph_text in main:
    i = main.index(emph_text)
    for ch in main[:i]: chars.append((ch, base_col))
    for ch in emph_text: chars.append((ch, emph_color))
    for ch in main[i+len(emph_text):]: chars.append((ch, base_col))
else:
    for ch in main: chars.append((ch, base_col))

MAXW = W - 300
fsize = int(188 * float(st["scale"]))
f = font(fsize)
def wrap_chars(chs, fnt):
    lines, cur, w = [], [], 0.0
    for ch, c in chs:
        cw = draw.textlength(ch, font=fnt)
        if w + cw > MAXW and cur:
            lines.append(cur); cur, w = [], 0.0
        cur.append((ch, c)); w += cw
    if cur: lines.append(cur)
    return lines
lines = wrap_chars(chars, f)
while len(lines) > 3 and fsize > 110:
    fsize -= 12; f = font(fsize); lines = wrap_chars(chars, f)
LH = int(fsize * 1.16)
x0 = 150
y = 250  # title near top, note-style
pos_y = [y + i*LH for i in range(len(lines))]
SW = max(10, int(fsize * 0.11))  # thick black outline

# category pill (above title)
cf = font(58, weight=800, family="sans")
pill_w = draw.textlength(category, font=cf) + 72
pgl = Image.new("RGBA",(W,H),(0,0,0,0))
ImageDraw.Draw(pgl).rounded_rectangle([x0, 120, x0+pill_w, 220], radius=50, fill=pill_col+(255,))
bg = Image.alpha_composite(bg, pgl.filter(ImageFilter.GaussianBlur(16)))
draw = ImageDraw.Draw(bg)
draw.rounded_rectangle([x0, 120, x0+pill_w, 220], radius=50, fill=pill_col+(255,))
draw.text((x0+36, 134), category, font=cf, fill=(16,18,30))

# accent glow behind title
gl = Image.new("RGBA",(W,H),(0,0,0,0)); gld = ImageDraw.Draw(gl)
for ln, ly in zip(lines, pos_y):
    cx = x0
    for ch, c in ln:
        gld.text((cx, ly), ch, font=f, fill=accent+(255,)); cx += draw.textlength(ch, font=f)
bg = Image.alpha_composite(bg, gl.filter(ImageFilter.GaussianBlur(26)))
draw = ImageDraw.Draw(bg)

# draw chars: heavy black outline + fill (gradient optional)
for ln, ly in zip(lines, pos_y):
    cx = x0
    for ch, c in ln:
        fill = c if grad_cols is None else (255,255,255)
        draw.text((cx, ly), ch, font=f, fill=fill, stroke_width=SW, stroke_fill=(8,10,22))
        cx += draw.textlength(ch, font=f)
# optional neon gradient overlay on glyphs (legacy flashy mode)
if grad_cols is not None:
    mask = Image.new("L",(W,H),0); mdd = ImageDraw.Draw(mask)
    for ln, ly in zip(lines, pos_y):
        cx = x0
        for ch, c in ln:
            mdd.text((cx, ly), ch, font=f, fill=255); cx += draw.textlength(ch, font=f)
    grad = Image.new("RGB",(W,H),grad_cols[1]); gdd = ImageDraw.Draw(grad)
    a,b,cc = grad_cols[0],grad_cols[1],grad_cols[2]
    for gx in range(0,W,2):
        t=gx/W
        col = tuple(int(a[i]+(b[i]-a[i])*(t/0.5)) for i in range(3)) if t<0.5 else tuple(int(b[i]+(cc[i]-b[i])*((t-0.5)/0.5)) for i in range(3))
        gdd.line([(gx,0),(gx,H)], fill=col, width=2)
    bg.paste(grad,(0,0),mask)

# English subtitle (optional)
draw = ImageDraw.Draw(bg)
if en_sub:
    ef = font(46, weight=700, family="sans")
    ey = pos_y[-1] + LH + 6
    draw.text((x0, ey), en_sub, font=ef, fill=(220,230,245), stroke_width=5, stroke_fill=(8,10,22))

# brand (bottom-right)
bf = font(46, weight=800, family="sans")
bt = "free-bizdocs.com"
bx = W - 150 - draw.textlength(bt, font=bf)
draw.text((bx, H-120), bt, font=bf, fill=(240,248,255), stroke_width=5, stroke_fill=(8,10,22))

os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
bg.convert("RGB").save(out, "WEBP", quality=86, method=6)
print("generated", out, bg.size, "photo" if photo is not None else "synthwave")
