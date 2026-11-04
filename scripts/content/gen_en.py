#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render EN blog drafts into en/blog/_drafts/<slug>.html matching the live template."""
import os, html as _h, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "out_en"
os.makedirs(OUT, exist_ok=True)

STYLE = """<style>
.ablog{max-width:760px;margin:0 auto;padding:0 20px 40px}
.bhero{margin-bottom:24px}
.bhero .in{max-width:760px;margin:0 auto;padding:16px 20px 0}
.bhero .bhero-img{display:block;width:100%;height:auto;aspect-ratio:1200/630;object-fit:cover;border-radius:16px;box-shadow:0 18px 42px -26px rgba(19,38,59,.55)}
.bhero .meta{font-size:13px;color:var(--mut,#5a6b80);margin:12px 2px 0}
.bhero .meta .cat{font-weight:800;text-transform:uppercase;letter-spacing:.04em;color:var(--ac,#1766e6);font-size:11.5px}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.crumb{max-width:760px;margin:0 auto;padding:14px 20px 0;font-size:12.5px;color:var(--faint,#93a3b5)}
.crumb a{color:var(--mut,#5a6b80);text-decoration:none}.crumb a:hover{text-decoration:underline}
.ablog .lead{font-size:16.5px;line-height:1.75;color:var(--ink);margin:0 0 22px}
.ablog h2{font-size:21px;font-weight:900;letter-spacing:-.01em;margin:30px 0 12px}
.ablog p{font-size:15.5px;line-height:1.8;color:#24303d;margin:0 0 15px}
.ablog ul{margin:0 0 18px;padding-left:22px}
.ablog li{font-size:15.5px;line-height:1.75;color:#24303d;margin:0 0 8px}
.ablog a{color:var(--ac,#1766e6);font-weight:600}
.ablog .note{background:#fff6ec;border:1px solid #f3dcc0;border-radius:12px;padding:13px 16px;margin:18px 0;font-size:14px;color:#7a5a2e;line-height:1.7}
.bfaq{max-width:760px;margin:36px auto 0;padding:0 20px}
.bfaq h2{font-size:21px;font-weight:900;margin:0 0 14px}
.bfaq .q{border-top:1px solid var(--bd,#e6e8ec);padding:16px 2px}
.bfaq .q h3{font-size:15.5px;font-weight:800;margin:0 0 6px}
.bfaq .q p{font-size:14.5px;color:var(--mut,#5a6b80);line-height:1.75;margin:0}
.brel{max-width:760px;margin:34px auto 0;padding:22px 20px 0;border-top:1px solid var(--bd,#e6e8ec)}
.brel h2{font-size:16px;font-weight:900;margin:0 0 12px}
.brel .rl{display:flex;flex-wrap:wrap;gap:10px}
.brel a{font-size:13.5px;font-weight:700;color:var(--ac,#1766e6);background:#eef4ff;border:1px solid #d9e6fb;border-radius:999px;padding:9px 15px;text-decoration:none}
.brel a:hover{background:#e2edff}
.bcta{max-width:760px;margin:26px auto 0;padding:0 20px}
.bcta a{display:block;text-align:center;background:linear-gradient(120deg,var(--ac,#1766e6),#2f8cf0);color:#fff;font-weight:800;font-size:15px;border-radius:13px;padding:15px;text-decoration:none}
</style>"""

HEADER = '''<header class="hdr"><div class="in">
  <a class="brand" href="/en/" style="text-decoration:none"><img src="/logo.png" alt="Free BizDoc" style="height:30px;width:auto;display:block"></a>
  <span class="sp"></span>
  <a class="pro" href="/?lang=ja" lang="ja" title="Japanese version">日本語</a>
</div></header>'''

FOOTER = '''<footer class="ft"><div class="in">
  <div class="cols">
    <div>
      <div class="brand"><img src="/logo.png" alt="Free BizDoc" style="height:26px;width:auto;display:block;filter:brightness(0) invert(1)"></div>
      <p>Free, no-sign-up business document generator. Invoices, estimates, receipts, purchase orders and packing slips as clean PDFs - generated in your browser.</p>
    </div>
    <div class="col">
      <h4>Free documents</h4>
      <a href="/en/invoice">Invoice</a>
      <a href="/en/estimate">Estimate / Quote</a>
      <a href="/en/receipt">Receipt</a>
      <a href="/en/purchase-order">Purchase Order</a>
      <a href="/en/packing-slip">Packing Slip / Delivery Note</a>
    </div>
    <div class="col">
      <h4>More</h4>
      <a href="/en/blog">Blog</a>
      <a href="/en/pricing">Pricing &amp; PRO</a>
      <a href="/en/account">Account</a>
      <a href="/?lang=ja" lang="ja">日本語</a>
      <a href="/en/contact">Contact</a>
      <a href="/en/privacy">Privacy policy</a>
    </div>
  </div>
  <div class="bot">&copy; 2026 Free BizDoc</div>
</div></footer>'''


def esc(s):
    return _h.escape(s, quote=True)


def jl(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def render(a):
    slug = a["slug"]
    title = a["title"]           # full card/h1 title
    ogtitle = a.get("ogtitle", title)
    desc = a["desc"]
    lead = a["lead"]
    url = f"https://free-bizdocs.com/en/blog/{slug}"
    img = f"https://free-bizdocs.com/en/blog/og/{slug}.jpg"
    c1 = a.get("c1", "#0e7490")
    c2 = a.get("c2", "#2bb3c0")

    card = (f"<!--ENCARD tag={a['tag']} | h2={a.get('cardh2', title)} | desc={a['carddesc']} "
            f"| c1={c1} | c2={c2}-->")

    sec_html = []
    for s in a["sections"]:
        sec_html.append(f'\n<h2>{esc(s["h2"])}</h2>\n{s["html"].strip()}')
    sections = "\n".join(sec_html)

    faq_ld = ", ".join(
        '{"@type": "Question", "name": "%s", "acceptedAnswer": {"@type": "Answer", "text": "%s"}}'
        % (jl(f["q"]), jl(f["a"])) for f in a["faq"]
    )
    faq_vis = "".join(
        f'<div class="q"><h3>{esc(f["q"])}</h3><p>{esc(f["a"])}</p></div>' for f in a["faq"]
    )
    rel = "".join(f'<a href="{r["href"]}">{esc(r["label"])}</a>' for r in a["related"])
    note = ("" if not a.get("note") else
            f'<p class="note">{a["note"]}</p>')
    cta_href = a["cta_href"]
    cta_label = a["cta_label"]
    cat = a["tag"]

    doc = f"""{card}
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}｜Free BizDoc</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{url}">
<link rel="alternate" hreflang="x-default" href="{url}">
<link rel="icon" href="/favicon.ico" sizes="any">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Free BizDoc">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{esc(ogtitle)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{img}">
<link rel="stylesheet" href="/suite.css?v=20261017d">
<script type="application/ld+json">{{"@context": "https://schema.org", "@type": "Article", "headline": "{jl(ogtitle)}", "description": "{jl(desc)}", "datePublished": "__PUBDATE__", "dateModified": "__PUBDATE__", "author": {{"@type": "Organization", "name": "Free BizDoc"}}, "publisher": {{"@type": "Organization", "name": "Free BizDoc", "logo": {{"@type": "ImageObject", "url": "https://free-bizdocs.com/logo.png"}}}}, "mainEntityOfPage": "{url}", "inLanguage": "en"}}</script>
<script type="application/ld+json">{{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://free-bizdocs.com/en/"}}, {{"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://free-bizdocs.com/en/blog"}}, {{"@type": "ListItem", "position": 3, "name": "{jl(ogtitle)}", "item": "{url}"}}]}}</script>
<script type="application/ld+json">{{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{faq_ld}]}}</script>
{STYLE}
</head>
<body>
{HEADER}
<nav class="crumb"><a href="/en/">Home</a> &rsaquo; <a href="/en/blog">Blog</a> &rsaquo; {esc(ogtitle)}</nav>
<section class="bhero"><div class="in"><img class="bhero-img" src="/en/blog/og/{slug}.jpg" alt="" width="1200" height="630" fetchpriority="high"><h1 class="sr-only">{esc(title)}</h1><div class="meta"><span class="cat">{esc(cat)}</span> &middot; Free BizDoc &middot; __PUBDATE_EN__</div></div></section>
<article class="ablog">
<p class="lead">{lead}</p>
{sections}
<p><a href="{cta_href}">{esc(cta_label)}</a></p>
</article>
<section class="bfaq"><h2>Frequently asked questions</h2>{faq_vis}</section>
<section class="brel"><h2>Related</h2><div class="rl">{rel}</div></section>
{FOOTER}
<script src="/en/siteheader-en.js?v=20261028r"></script>
</body>
</html>"""
    return doc


def main():
    import en_data
    arts = en_data.ARTICLES
    for a in arts:
        with open(os.path.join(OUT, a["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(render(a))
    print(f"wrote {len(arts)} EN drafts to {OUT}")


if __name__ == "__main__":
    main()
