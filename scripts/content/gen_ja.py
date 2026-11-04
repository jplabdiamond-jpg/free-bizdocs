#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render JA blog drafts into blog/_drafts/<slug>.html matching the live template."""
import os, json, html as _h, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "out_ja"
os.makedirs(OUT, exist_ok=True)

STYLE = """<style>
.bgwrap{max-width:860px;margin:0 auto;padding:28px 20px 0}
.bc{font-size:12.5px;color:var(--faint);margin-bottom:6px}.bc a{color:var(--mut);text-decoration:none}.bc a:hover{text-decoration:underline}
.art{max-width:720px;margin:0 auto;padding:4px 20px 50px}
.art h1{font-size:clamp(23px,4vw,33px);font-weight:900;line-height:1.35;letter-spacing:-.01em;margin:0 0 14px}
.art .eyecatch{margin:0 0 20px}.art .eyecatch img{width:100%;height:auto;border-radius:12px;display:block;box-shadow:0 10px 30px -12px rgba(19,38,59,.4)}
.art .meta{font-size:13px;color:var(--faint);margin:0 0 26px}
.art .lead{font-size:16px;line-height:1.9;color:#2b3a4b;margin:0 0 22px}
.art h2{font-size:clamp(19px,3vw,23px);font-weight:900;margin:38px 0 12px;padding-top:14px;border-top:2px solid var(--ac-s)}
.art h3{font-size:16.5px;font-weight:800;margin:24px 0 8px}
.art p{font-size:15.5px;line-height:1.95;color:#243;margin:0 0 16px}
.art ul,.art ol{font-size:15.5px;line-height:1.9;color:#243;margin:0 0 16px;padding-left:1.5em}
.art li{margin-bottom:6px}
.art .callout{background:var(--soft,#f4f8ff);border:1px solid var(--bd);border-left:4px solid var(--ac);border-radius:10px;padding:14px 16px;margin:0 0 18px;font-size:14.5px;line-height:1.8}
.art table{width:100%;border-collapse:collapse;margin:0 0 18px;font-size:14px}
.art th,.art td{border:1px solid var(--bd);padding:8px 10px;text-align:left}
.art th{background:var(--surf2,#f7fafe);font-weight:700}
.art .cta{display:block;background:linear-gradient(120deg,#1766e6,#2f8cf0 60%,#36b0f0);color:#fff;text-decoration:none;text-align:center;font-weight:800;font-size:16px;padding:16px;border-radius:12px;margin:26px 0;box-shadow:0 8px 22px -6px rgba(23,102,230,.5)}
.art .note{font-size:12.5px;color:var(--faint);margin-top:28px;border-top:1px solid var(--bd);padding-top:14px;line-height:1.7}
.art .rel{margin-top:14px}.art .rel b{display:block;font-size:13px;color:var(--mut);margin-bottom:6px}
.art .rel a{display:inline-block;margin:0 12px 8px 0;font-size:13.5px;color:var(--ac)}
</style>"""

HEADER = '<header class="hdr"><div class="in"><a class="brand" href="/"><img src="/logo.png" alt="Free BizDocs" style="height:30px;width:auto;display:block"></a><span class="sp"></span><nav class="nav"><a href="/invoice">請求書ほか</a><a href="/rirekisho">履歴書</a><a href="/blog">お役立ち</a><a href="/pricing">料金・PRO</a></nav></div></header>'

FOOTER = '''<footer class="ft"><div class="in">
  <div class="row"><a class="brand" href="/" style="display:inline-flex"><span class="mk">書</span><span class="nm" style="color:#fff"><b class="bn">Free BizDoc</b><em class="sb">無料ビジネス書類メーカー</em></span></a></div>
  <div class="row"><a href="/invoice">請求書</a> ・ <a href="/quote">見積書</a> ・ <a href="/delivery">納品書</a> ・ <a href="/purchase-order">発注書</a> ・ <a href="/receipt">領収書</a> ・ <a href="/rirekisho">履歴書</a> ・ <a href="/shokumu">職務経歴書</a> ・ <a href="/soufu">送付状</a> ・ <a href="/taishoku">退職届</a></div>
  <div class="row"><a href="/blog">お役立ち記事</a> ・ <a href="/feedback">ご意見・ご要望</a> ・ <a href="/contact">お問い合わせ</a> ・ <a href="/tokushoho">特定商取引法に基づく表記</a> ・ <a href="/privacy">プライバシーポリシー</a></div>
  <div class="row" style="color:#8097ad">© 2026 Free BizDoc</div>
</div></footer>'''


def esc(s):
    return _h.escape(s, quote=True)


def jsonld_str(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def render(a):
    slug = a["slug"]
    full = a["title"]
    cardh2 = a.get("cardh2", full.split("｜")[0])
    carddesc = a["carddesc"]
    metadesc = a.get("metadesc", carddesc)
    lead = a["lead"]
    url = f"https://free-bizdocs.com/blog/{slug}"
    img = f"https://free-bizdocs.com/blog/img/{slug}.webp"

    # CARD comment
    card_bits = [f"tag={a['tag']}", f"h2={cardh2}", f"desc={carddesc}"]
    if a.get("emph"):
        card_bits.append(f"emph={a['emph']}")
    if a.get("emphcolor"):
        card_bits.append(f"emphcolor={a['emphcolor']}")
    if a.get("en"):
        card_bits.append(f"en={a['en']}")
    if a.get("font"):
        card_bits.append(f"font={a['font']}")
    if a.get("pill"):
        card_bits.append(f"pill={a['pill']}")
    card = "<!--CARD " + " | ".join(card_bits) + "-->"

    # sections
    sec_html = []
    for s in a["sections"]:
        sec_html.append(f'\n<h2>{esc(s["h2"])}</h2>\n{s["html"].strip()}')
    sections = "\n".join(sec_html)

    # FAQ
    faq_ld = ",".join(
        '{"@type":"Question","name":"%s","acceptedAnswer":{"@type":"Answer","text":"%s"}}'
        % (jsonld_str(f["q"]), jsonld_str(f["a"])) for f in a["faq"]
    )
    faq_vis = "\n".join(f'<h3>{esc(f["q"])}</h3>\n<p>{esc(f["a"])}</p>' for f in a["faq"])

    rel = "".join(f'<a href="{r["href"]}">{esc(r["label"])}</a>' for r in a["related"])
    note = a.get("note", "本記事は一般的な実務の解説です。最終的なご判断は彜要に応じて専門家にご確認ください。")
    cta_href = a.get("cta_href", a.get("tool", "/invoice"))
    cta_label = a["cta_label"]
    bc_label = cardh2

    doc = f"""{card}
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full)}｜Free BizDoc</title>
<meta name="description" content="{esc(metadesc)}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="robots" content="index,follow">
<link rel="stylesheet" href="/landing.css?v=20261016c">
{STYLE}
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(full)}｜Free BizDoc">
<meta property="og:description" content="{esc(carddesc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="2560">
<meta property="og:image:height" content="1440">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{img}">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Article","headline":"{jsonld_str(full)}","description":"{jsonld_str(carddesc)}","image":"{img}","author":{{"@type":"Organization","name":"Free BizDoc"}},"publisher":{{"@type":"Organization","name":"Free BizDoc"}},"datePublished":"__PUBDATE__","dateModified":"__PUBDATE__","mainEntityOfPage":"{url}"}}</script>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"ホーム","item":"https://free-bizdocs.com/"}},{{"@type":"ListItem","position":2,"name":"お役立ち","item":"https://free-bizdocs.com/blog"}},{{"@type":"ListItem","position":3,"name":"{jsonld_str(bc_label)}","item":"{url}"}}]}}</script>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{faq_ld}]}}</script>
</head>
<body>
{HEADER}
<div class="bgwrap"><nav class="bc"><a href="/">ホーム</a> › <a href="/blog">お役立ち</a> › {esc(bc_label)}</nav></div>
<article class="art">
<h1>{esc(full)}</h1>
<figure class="eyecatch"><img src="/blog/img/{slug}.webp" alt="{esc(full)}" width="1200" height="675" loading="eager"></figure>
<p class="meta">更新日：__PUBDATE_JP__ ・ Free BizDoc 編集部</p>
<p class="lead">{lead}</p>
{sections}

<h2>無料ツールで作成</h2>
<p>{a.get('tool_line', 'Free BizDoc なら、登録不要・無料でその場で PDF ダウンロードできます。スマホからも作成できます。')}</p>
<a class="cta" href="{cta_href}">{esc(cta_label)}</a>

<h2>よくある質問</h2>
{faq_vis}

<div class="rel"><b>関連ツール・記事</b>{rel}</div>
<p class="note">{esc(note)}</p>
</article>
{FOOTER}
<script src="/siteheader.js?v=20261019en"></script>
</body></html>"""
    return doc


def main():
    import ja_data
    arts = ja_data.ARTICLES
    for a in arts:
        doc = render(a)
        with open(os.path.join(OUT, a["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(doc)
    print(f"wrote {len(arts)} JA drafts to {OUT}")


if __name__ == "__main__":
    main()
