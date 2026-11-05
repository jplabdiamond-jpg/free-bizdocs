# -*- coding: utf-8 -*-
"""New eyecatch layout: Free BizDoc logo + gothic white title + marker highlight
+ fitting photo background + domain. Shared core for JA (2560x1440) and EN (1200x630).
"""
import os, io, time, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
def _find(name, extra=()):
    for p in [os.path.join(HERE, name)] + [os.path.join(HERE, e, name) for e in extra]:
        if os.path.exists(p): return p
    return os.path.join(HERE, name)
FONT_SANS = _find("NotoSansJP-VF.ttf", ("..",))
LOGO = _find("logo.png", ("..",))

def hx(s):
    s = str(s).lstrip("#"); return (int(s[0:2],16), int(s[2:4],16), int(s[4:6],16))

def font(size, weight=800):
    f = ImageFont.truetype(FONT_SANS, size)
    try: f.set_variation_by_axes([weight])
    except Exception: pass
    return f

# ---------- background ----------
def fetch(subject, seed, W, H, prompt=None):
    if prompt is None:
        prompt = (subject + ", hyperrealistic photograph, professional desk scene, "
                  "shallow depth of field, cinematic soft lighting, clean, "
                  "no text, no words, no letters, no watermark")
    for model, to in [("flux",70),("turbo",45),("flux",70),("turbo",40)]:
        try:
            url=("https://image.pollinations.ai/prompt/"+urllib.parse.quote(prompt)
                 +"?width=%d&height=%d&seed=%d&nologo=true&model=%s"%(min(W,1280),min(H,720),seed%100000,model))
            req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            im=Image.open(io.BytesIO(urllib.request.urlopen(req,timeout=to).read())).convert("RGB")
            if im.width<400: raise ValueError("small")
            im=im.crop((0,0,im.width,int(im.height*0.94)))
            return _cover(im,W,H)
        except Exception as e:
            import sys; sys.stderr.write("poll(%s) %s\n"%(model,e)); time.sleep(2)
    return None

def _cover(im,W,H):
    r=max(W/im.width,H/im.height)
    im=im.resize((int(im.width*r),int(im.height*r)),Image.LANCZOS)
    x=(im.width-W)//2; y=(im.height-H)//2
    return im.crop((x,y,x+W,y+H))

def fallback_bg(accent, seed, W, H):
    base=Image.new("RGB",(W,H),(14,20,32)); d=ImageDraw.Draw(base)
    for i in range(H):
        t=i/H; d.line([(0,i),(W,i)],fill=(int(12+10*t),int(18+16*t),int(30+26*t)))
    glow=Image.new("RGB",(W,H),(0,0,0)); gd=ImageDraw.Draw(glow)
    gd.ellipse([W*0.45,-H*0.3,W*1.2,H*0.6],fill=tuple(int(c*0.33) for c in accent))
    return Image.blend(base,glow.filter(ImageFilter.GaussianBlur(int(W*0.14))),0.5)

def grade(im, W, H):
    im=ImageEnhance.Brightness(im).enhance(0.9)
    im=ImageEnhance.Color(im).enhance(0.95)
    # even dark scrim for legibility, slightly stronger on the left and bottom
    ov=Image.new("L",(W,H),0); px=ov.load()
    for x in range(W):
        lt=1-(x/W)
        a_left=150*(lt**1.3)
        for y in range(H):
            bt=y/H
            a=int(min(235, 70 + a_left + 70*(bt**2.2)))
            px[x,y]=a
    dark=Image.new("RGB",(W,H),(8,13,22))
    return Image.composite(dark, im, ov).convert("RGBA")

# ---------- logo ----------
def logo_plate(target_h):
    lg=Image.open(LOGO).convert("RGBA")
    # key out near-white background if opaque
    if lg.getchannel("A").getextrema()[0]==255:
        px=lg.load()
        for y in range(lg.height):
            for x in range(lg.width):
                r,g,b,a=px[x,y]
                if r>240 and g>240 and b>240: px[x,y]=(r,g,b,0)
    r=target_h/lg.height
    lg=lg.resize((int(lg.width*r),target_h),Image.LANCZOS)
    pad=int(target_h*0.42); rad=int(target_h*0.34)
    plate=Image.new("RGBA",(lg.width+pad*2, lg.height+pad*2),(0,0,0,0))
    d=ImageDraw.Draw(plate)
    d.rounded_rectangle([0,0,plate.width-1,plate.height-1],radius=rad,fill=(255,255,255,245))
    plate.alpha_composite(lg,(pad,pad))
    return plate

def logo_white(target_h):
    lg=Image.open(LOGO).convert("RGBA")
    if lg.getchannel("A").getextrema()[0]==255:
        px=lg.load()
        for y in range(lg.height):
            for x in range(lg.width):
                r,g,b,a=px[x,y]
                px[x,y]=(255,255,255,0 if (r>240 and g>240 and b>240) else 255)
    else:
        white=Image.new("RGBA",lg.size,(255,255,255,0))
        white.putalpha(lg.getchannel("A"));
        wpx=white.load()
        for y in range(lg.height):
            for x in range(lg.width):
                _,_,_,a=lg.getpixel((x,y)); wpx[x,y]=(255,255,255,a)
        lg=white
    r=target_h/lg.height
    return lg.resize((int(lg.width*r),target_h),Image.LANCZOS)

# ---------- title wrapping with marker runs (natural breaks) ----------
_BRK_AFTER=set("｜、。，？！・／/）】」』〉》")
_BRK_BEFORE=set("（【「『〈《")

def _allowed_breaks(title, emph):
    ok=set()
    for i in range(1,len(title)):
        if title[i-1] in _BRK_AFTER or title[i] in _BRK_BEFORE:
            ok.add(i)
    if emph:
        s=title.find(emph)
        if s>=0:
            for i in range(s+1, s+len(emph)): ok.discard(i)
    return ok

_STRIP_END=set("｜／/・　")
def _runs_from(text, start, marks):
    n=len(text)
    while n>0 and text[n-1] in _STRIP_END: n-=1
    text=text[:n]
    runs=[]; buf=""; cm=None
    for j,ch in enumerate(text):
        m=marks[start+j]
        if cm is None: cm=m
        if m==cm: buf+=ch
        else: runs.append((buf,cm)); buf=ch; cm=m
    if buf: runs.append((buf,cm))
    return runs

def wrap_ja(title, emph, fnt, max_w, draw, max_lines=3):
    """Wrap a JA title at natural break points only; marker on first emph run."""
    marks=[False]*len(title)
    if emph:
        i=title.find(emph)
        if i>=0:
            for k in range(i,i+len(emph)): marks[k]=True
    allowed=_allowed_breaks(title, emph)
    def W(a,b): return draw.textbbox((0,0),title[a:b],font=fnt)[2]
    lines=[]; a=0; n=len(title)
    while a<n:
        # longest end that fits
        hi=a+1
        while hi<=n and W(a,hi)<=max_w: hi+=1
        end=hi-1 if hi-1>a else a+1
        if end>=n:
            end=n
        else:
            # pull back to the last allowed break <= end
            cand=[b for b in allowed if a<b<=end]
            if cand: end=max(cand)
            # else hard break at end (rare; font-fit avoids this)
        lines.append(_runs_from(title[a:end], a, marks))
        a=end
        if len(lines)>=max_lines and a<n:
            # overflow: dump remainder on last line
            lines[-1]=_runs_from(title[a-0:a], a, marks) if False else lines[-1]
            rest=_runs_from(title[a:n], a, marks)
            lines[-1]=lines[-1]+rest
            break
    return lines

def fit_ja(title, emph, draw, H, max_w,
           fracs=(0.100,0.092,0.084,0.076,0.069,0.062)):
    def fits(lines,f):
        return all(draw.textbbox((0,0),"".join(t for t,_ in ln),font=f)[2]<=max_w for ln in lines)
    # prefer the largest font that fits in <=2 lines (down to a sensible floor)
    for fr in fracs:
        if fr < 0.075: break
        tp=int(H*fr); f=font(tp,800)
        lines=wrap_ja(title, emph, f, max_w, draw, max_lines=2)
        if len(lines)<=2 and fits(lines,f):
            return lines, tp
    # otherwise the largest font that fits in <=3 lines
    for fr in fracs:
        tp=int(H*fr); f=font(tp,800)
        lines=wrap_ja(title, emph, f, max_w, draw, max_lines=3)
        if len(lines)<=3 and fits(lines,f):
            return lines, tp
    tp=int(H*fracs[-1])
    return wrap_ja(title, emph, font(tp,800), max_w, draw, max_lines=3), tp

# ---------- compose (centered layout) ----------
def _line_w(d, runs, tf):
    return sum(d.textbbox((0,0),t,font=tf)[2] for t,_ in runs)

def compose(W,H, bg, kicker, lines, accent, marker, domain, logo_mode="plate",
            title_px=None, line_gap=None):
    im = bg.copy()
    d = ImageDraw.Draw(im)
    cx = W//2
    # logo (top-center)
    topM = int(H*0.072)
    logo = logo_plate(int(H*0.092)) if logo_mode=="plate" else logo_white(int(H*0.076))
    im.alpha_composite(logo,(cx - logo.width//2, topM))
    # kicker (centered)
    kf = font(int(H*0.027), 700)
    ky = topM + logo.height + int(H*0.05)
    kw = d.textbbox((0,0),kicker,font=kf)[2]
    d.text((cx - kw//2, ky), kicker, font=kf, fill=(216,226,238,255))
    # title block (centered, vertically centered in lower-middle band)
    tp = title_px or int(H*0.092)
    tf = font(tp, 800)
    lg_ = line_gap if line_gap is not None else int(tp*0.34)
    ink=(21,32,43,255)
    total_h = len(lines)*tp + (len(lines)-1)*lg_
    band_top = ky + int(H*0.07)
    band_bot = H - int(H*0.14)
    y = band_top + max(0, ((band_bot-band_top) - total_h)//2)
    for runs in lines:
        lw = _line_w(d, runs, tf)
        x0 = cx - lw//2
        # marker rects
        xx=x0
        for text,marked in runs:
            w=d.textbbox((0,0),text,font=tf)[2]
            if marked and text.strip():
                bb=tf.getbbox(text)
                top=y+bb[1]; bot=y+bb[3]
                px=int(tp*0.12); py=int(tp*0.14)
                d.rounded_rectangle([xx-px, top-py, xx+w+px, bot+py],
                                    radius=int(tp*0.13), fill=marker+(255,))
            xx+=w
        # text
        xx=x0
        for text,marked in runs:
            w=d.textbbox((0,0),text,font=tf)[2]
            if marked:
                d.text((xx,y), text, font=tf, fill=ink)
            else:
                d.text((xx+2,y+2), text, font=tf, fill=(0,0,0,110))
                d.text((xx,y), text, font=tf, fill=(255,255,255,255))
            xx+=w
        y += tp + lg_
    # domain (centered, bottom) with accent tick
    df = font(int(H*0.03), 700)
    dw = d.textbbox((0,0),domain,font=df)[2]
    dy = H - int(H*0.088)
    tick_w = int(W*0.009); gap=int(W*0.011)
    gx = cx - (dw + tick_w + gap)//2
    d.rectangle([gx, dy+int(H*0.004), gx+tick_w, dy+int(H*0.03)], fill=accent+(255,))
    d.text((gx+tick_w+gap, dy), domain, font=df, fill=(210,220,232,255))
    return im.convert("RGB")
