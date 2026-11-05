#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JA blog eyecatch generator -> webp 2560x1440 (Free BizDoc column style).
Layout: white logo plate (top-center) + gothic white title (centered, natural
wrapping) + marker highlight on the emphasized phrase + fitting hyperreal photo
background + domain. Colors come from the fixed per-category palette.

  python3 scripts/gen-eyecatch.py <slug> <title> <category> <out_webp> [style_json]
style_json (all optional): emph (phrase to highlight), pill (marker color),
  emphcolor (alt marker color), colors (ignored), en (ignored), font (ignored).
Fonts (NotoSansJP-VF.ttf) and logo (../logo.png) are bundled / in the repo.
"""
import sys, os, json, random, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import thumb_core as T
from PIL import ImageDraw

slug, title, category, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
STYLE = {}
if len(sys.argv) > 5 and sys.argv[5].strip():
    try: STYLE = json.loads(sys.argv[5])
    except Exception as e: sys.stderr.write("style parse error: %s\n" % e)

W, H = 2560, 1440
seed = int(hashlib.md5(slug.encode("utf-8")).hexdigest(), 16) % (2**31)
rnd = random.Random(seed)

# fixed per-category palette: accent (tick/kicker), pill (marker)
PRESET = {
 "請求書":   {"accent":"#1766e6","pill":"#ffdd00"},
 "領収書":   {"accent":"#0f9d8f","pill":"#ffdd00"},
 "見積書":   {"accent":"#7a52ff","pill":"#ffdd00"},
 "履歴書":   {"accent":"#e68a1c","pill":"#19e0ff"},
 "職務経歴書":{"accent":"#1f8fff","pill":"#19e0ff"},
 "退職":     {"accent":"#e64664","pill":"#19e0ff"},
 "税金・計算":{"accent":"#e64664","pill":"#ffdd00"},
 "税・経理":  {"accent":"#e64664","pill":"#ffdd00"},
 "転職・就活":{"accent":"#f07c1e","pill":"#19e0ff"},
 "電子印鑑":  {"accent":"#e6468f","pill":"#19e0ff"},
 "発注書":    {"accent":"#0f9d8f","pill":"#ffdd00"},
}
pr = PRESET.get(category, {"accent":"#1766e6","pill":"#ffdd00"})
accent = T.hx(STYLE.get("accent", pr["accent"]))
marker = T.hx(STYLE.get("pill") or STYLE.get("emphcolor") or pr["pill"])
emph = STYLE.get("emph", "")
kicker = category + "コラム"

SUBJECT = {
 "請求書":"invoice documents with a calculator and a pen",
 "領収書":"paper receipts with a red stamp and a pen",
 "見積書":"quotation documents with a pen and a tablet",
 "履歴書":"a Japanese resume form with a pen",
 "職務経歴書":"career history documents with a laptop",
 "退職":"a resignation letter and a white envelope",
 "税金・計算":"tax documents with a calculator and stacked coins",
 "税・経理":"tax and accounting documents with a calculator and stacked coins",
 "転職・就活":"resume and job-hunting documents with a laptop",
 "電子印鑑":"a red Japanese hanko stamp with an ink pad and business documents",
 "発注書":"a purchase order document with a pen and a laptop",
}
subject = SUBJECT.get(category, "business documents with a laptop and a calculator")
COMPOS = ["top-down flat lay from directly above","straight-on eye-level view",
          "close-up macro shot","wide desk scene","overhead 45-degree view",
          "bird's-eye view","diagonal side perspective","off-center composition"]
ARRANGE = ["a neat stack of","scattered","an organized spread of","a few","fanned-out"]
LIGHT = ["bright soft daylight","airy window light","clean studio lighting","soft diffused light"]
prompt = ("%s of %s %s on a modern desk, %s, hyperrealistic photograph, ultra detailed, "
          "clean, professional, no text, no words, no letters, no watermark"
          % (rnd.choice(COMPOS), rnd.choice(ARRANGE), subject, rnd.choice(LIGHT)))

im = T.fetch(subject, seed, W, H, prompt=prompt)
if im is None:
    im = T.fallback_bg(accent, seed, W, H)
bg = T.grade(im, W, H)

d = ImageDraw.Draw(bg)
lines, tp = T.fit_ja(title, emph, d, H, int(W*0.86))
res = T.compose(W, H, bg, kicker, lines, accent, marker, "free-bizdocs.com",
                logo_mode="plate", title_px=tp)
res.save(out, "WEBP", quality=88, method=6)
print("generated", out, "(%dx%d) lines=%d tp=%d" % (W, H, len(lines), tp))
