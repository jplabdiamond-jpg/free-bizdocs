#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EN blog OG images (1200x630) in the Free BizDoc column style:
white logo plate + category kicker + gothic white title (line 1) with a marker
highlight on line 2 + fitting hyperreal photo background + domain.
Colors use each article's fixed c1/c2.
  python3 gen_en_og.py <out_dir>     # reads en_data.ARTICLES
"""
import os, sys, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)                      # for en_data
sys.path.insert(0, os.path.join(HERE, ".."))  # for thumb_core (scripts/)
import thumb_core as T

OUT = sys.argv[1] if len(sys.argv) > 1 else "out_og"
os.makedirs(OUT, exist_ok=True)
W, H = 1200, 630

def render(a):
    slug = a["slug"]
    seed = int(hashlib.md5(slug.encode()).hexdigest(), 16) % (2**31)
    c2 = T.hx(a.get("c2", "#2bb3c0"))
    im = T.fetch(a["subject"], seed, W, H)
    if im is None:
        im = T.fallback_bg(c2, seed, W, H)
    bg = T.grade(im, W, H)
    lines = [[(a["ogline1"], False)], [(a["ogline2"], True)]]
    res = T.compose(W, H, bg, a["oglabel"].upper(), lines, c2, c2, "free-bizdocs.com",
                    logo_mode="plate", title_px=int(H*0.115), line_gap=int(H*0.034))
    res.save(os.path.join(OUT, slug + ".jpg"), "JPEG", quality=86, optimize=True)
    print("og:", slug)

def main():
    import en_data
    want = set(sys.argv[2:])  # optional slug filter
    for a in en_data.ARTICLES:
        if want and a["slug"] not in want:
            continue
        render(a)
    print("done EN og")

if __name__ == "__main__":
    main()
